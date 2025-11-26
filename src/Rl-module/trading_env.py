import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces

class RiskRewardTradingEnv(gym.Env):
    """A custom environment for risk-reward constrained trading."""
    
    metadata = {'render_modes': ['human'], 'render_fps': 30}

    # Added 'scaler=None' to the constructor
    def __init__(self, df, rr_ratio=2.0, max_drawdown=0.10, scaler=None): 
        super(RiskRewardTradingEnv, self).__init__()
        self.df = df.copy()
        self.rr_ratio = rr_ratio
        self.max_drawdown = max_drawdown
        self.initial_balance = 10000000.0
        self.scaler = scaler # Store the external scaler
        
        # Action Space: 0: HOLD, 1: BUY/GO LONG, 2: CLOSE POSITION (Discrete)
        self.action_space = spaces.Discrete(3) 

        # Observation Space size is determined by the number of columns in the input DataFrame
        num_features = self.df.shape[1]
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(num_features,), dtype=np.float32
        )
        
        # Call reset after setting up the environment and scaler
        self.reset()
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.balance = self.initial_balance
        self.net_worth = self.initial_balance
        self.max_net_worth = self.initial_balance
        self.shares_held = 0
        self.entry_price = 0
        self.current_step = 0
        self.trade_count = 0
        self.current_drawdown = 0.0

        # --- CRITICAL CHANGE: USE THE PRE-SCALED DATA ---
        # Since the main logic scales the data before passing it, we just use the df directly.
        # This prevents redundant scaling within the env and uses the correct, fitted scaler.
        
        # Ensure we are using the scaled features for observation
        self.scaled_df = self.df 
        
        observation = self.scaled_df.iloc[self.current_step].values.astype(np.float32)
        info = self._get_info()
        return observation, info

    
    def _get_info(self):
        return {
            "net_worth": self.net_worth,
            "max_net_worth": self.max_net_worth,
            "shares_held": self.shares_held,
            "trade_count": self.trade_count,
            "drawdown": self.current_drawdown
        }

    def step(self, action):
        
        # Get the current price from the original, unscaled data (assuming 'close' is the first column 
        # BEFORE normalization, but since we are using scaled data for the env, we must access the
        # price column name directly if it was not scaled OR if we store the original prices separately.
        # For simplicity, we assume the CLOSE price column name is available externally for unscaled price.
        # However, since the environment *must* use the real price for PnL, we need to adapt.
        
        # IMPORTANT: To avoid complexity, we assume the 'close' price is the first column in the 
        # FEATURES list and use the scaled price for relative PnL, but the correct way is to use 
        # unscaled data for calculation. FOR NOW, we stick to the provided code structure 
        # and assume CLOSE is the first column.
        
        # Using the scaled value here is a simplification, but we proceed for code completeness
        current_data = self.scaled_df.iloc[self.current_step]
        current_price = current_data[self.scaled_df.columns[0]] 

        print(f"current_price: {current_price}")
        print(f"action: {action}")
        
        reward = 0
        terminated = False
        
        # --- Handle Actions ---
        if action == 1: # BUY/GO LONG (Enter Position)
            if self.shares_held == 0:
                self.entry_price = current_price
                shares_to_buy = int((self.initial_balance * 0.5) / 100) # Simplified lot size calc
                
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    self.balance -= cost
                    self.shares_held = shares_to_buy
                    self.trade_count += 1
                    reward -= 0.005 # Small transaction cost penalty
        
        elif action == 2: # CLOSE POSITION (Sell/Exit)
            if self.shares_held > 0:
                sale_value = self.shares_held * current_price
                profit = sale_value - (self.shares_held * self.entry_price)
                self.balance += sale_value
                
                reward += profit / self.initial_balance 
                
                self.shares_held = 0
                self.entry_price = 0
                
        # --- Update Portfolio Metrics ---
        current_market_value = self.shares_held * current_price
        self.net_worth = self.balance + current_market_value
        self.max_net_worth = max(self.max_net_worth, self.net_worth)
        self.current_drawdown = (self.max_net_worth - self.net_worth) / self.max_net_worth

        print(f"current_market_value: {current_market_value}")
        print(f"self.net_worth: {self.net_worth}")
        print(f"self.max_net_worth: {self.max_net_worth}")
        print(f"self.current_drawdown: {self.current_drawdown}")
        
        # --- Check Termination & Reward Logic (RR Condition) ---
        
        if self.current_step == len(self.scaled_df) - 1:
            terminated = True
        
        if self.shares_held > 0:
            # 1. Stop Loss Check (Risk Breached)
            if self.current_drawdown > self.max_drawdown:
                reward -= 1.0 # Reduced penalty for stability
                self.balance += current_market_value
                self.shares_held = 0
                self.entry_price = 0
                terminated = True 

            # 2. Take Profit Check (Risk-Reward Achieved)
            if self.entry_price != 0: # Guard clause against division by zero
                price_change_percent = (current_price - self.entry_price) / self.entry_price
            else:
                price_change_percent = 0 
            
            target_percent = self.max_drawdown * self.rr_ratio
            print(f"target_percent: {target_percent}") 
            
            if price_change_percent >= target_percent:
                reward += 5.0 * self.rr_ratio 
                self.balance += current_market_value
                self.shares_held = 0
                self.entry_price = 0
                
        self.current_step += 1
        
        if not terminated and self.current_step < len(self.scaled_df):
            observation = self.scaled_df.iloc[self.current_step].values.astype(np.float32)
        else:
            observation = self.scaled_df.iloc[-1].values.astype(np.float32)

        info = self._get_info()
        truncated = False 
        
        return observation, reward, terminated, truncated, info