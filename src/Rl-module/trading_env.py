import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces

class RiskRewardTradingEnv(gym.Env):
    """A custom environment for risk-reward constrained trading."""
    
    metadata = {'render_modes': ['human'], 'render_fps': 30}

    def __init__(self, df, rr_ratio=2.0, max_drawdown=0.10, scaler=None): 
        super(RiskRewardTradingEnv, self).__init__()
        self.df = df.copy()
        self.rr_ratio = rr_ratio
        self.max_drawdown = max_drawdown
        self.initial_balance = 10000000.0
        self.scaler = scaler # Store the external scaler
        
        # --- History Tracking Attributes ---
        self.net_worth_history = []
        self.drawdown_history = []
        self.reward_history = []
        self.trades_log = [] # To store details of every executed trade
        # ----------------------------------
        
        # Action Space: 0: HOLD, 1: BUY/GO LONG, 2: CLOSE POSITION (Discrete)
        self.action_space = spaces.Discrete(3) 

        # Observation Space size is determined by the number of columns in the input DataFrame
        num_features = self.df.shape[1]
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(num_features,), dtype=np.float32
        )
        
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
        self.entry_step = 0 # Track the step when a trade was opened

        # Reset history
        self.net_worth_history = [self.initial_balance]
        self.drawdown_history = [0.0]
        self.reward_history = [0.0]
        self.trades_log = []
        
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
        
    def _close_position_and_log(self, current_price, outcome_reason):
        """Helper function to execute a sale, calculate P&L, and log the trade."""
        
        # Calculate profit/loss
        sale_value = self.shares_held * current_price
        cost = self.shares_held * self.entry_price
        profit = sale_value - cost
        
        # Calculate reward (normalized to initial balance for the RL agent)
        reward = profit / self.initial_balance 
        
        # Log the trade details
        trade_info = {
            "exit_step": self.current_step,
            "entry_step": self.entry_step,
            "duration": self.current_step - self.entry_step,
            "entry_price": self.entry_price,
            "exit_price": current_price,
            "profit_abs": profit,
            "profit_pct": (profit / cost) if cost != 0 else 0,
            "outcome": outcome_reason,
            "shares": self.shares_held
        }
        self.trades_log.append(trade_info)

        # Update balance and reset position
        self.balance += sale_value
        self.shares_held = 0
        self.entry_price = 0
        self.entry_step = 0
        
        return reward


    def step(self, action):
        
        # Price is assumed to be UN-SCALED (due to fix in train_and_backtest.py)
        current_data = self.scaled_df.iloc[self.current_step]
        current_price = current_data[self.scaled_df.columns[0]] 

        reward = 0
        terminated = False
        
        # --- Handle Actions ---
        if action == 1: # BUY/GO LONG (Enter Position)
            if self.shares_held == 0:
                self.entry_price = current_price
                # Investing 50% of initial balance
                shares_to_buy = int((self.initial_balance * 0.5) / current_price) 
                
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    self.balance -= cost
                    self.shares_held = shares_to_buy
                    self.trade_count += 1
                    self.entry_step = self.current_step
                    # Small transaction cost penalty 
                    reward -= 0.00005 
        
        elif action == 2: # CLOSE POSITION (Sell/Exit)
            if self.shares_held > 0:
                reward += self._close_position_and_log(current_price, "CLOSED_BY_AGENT")
                
        # --- Update Portfolio Metrics ---
        current_market_value = self.shares_held * current_price
        self.net_worth = self.balance + current_market_value
        self.max_net_worth = max(self.max_net_worth, self.net_worth)
        self.current_drawdown = (self.max_net_worth - self.net_worth) / self.max_net_worth

        # --- Check Termination & Reward Logic (SL/TP Condition) ---
        
        # 1. End of Data Check
        if self.current_step == len(self.scaled_df) - 1:
            if self.shares_held > 0:
                 # Close remaining position at the final price
                reward += self._close_position_and_log(current_price, "END_OF_DATA") 
            terminated = True
        
        if self.shares_held > 0:
            
            # Check Stop Loss (Risk Breached)
            if self.current_drawdown > self.max_drawdown:
                reward -= 1.0 # Heavy penalty for hitting the hard stop-loss
                reward += self._close_position_and_log(current_price, "STOP_LOSS")
                
            # Check Take Profit (Reward Achieved)
            if self.entry_price != 0: 
                price_change_percent = (current_price - self.entry_price) / self.entry_price
            else:
                price_change_percent = 0 
            
            # The percentage required to hit the Risk-Reward ratio
            target_percent = self.max_drawdown * self.rr_ratio
            
            if price_change_percent >= target_percent:
                reward += 1.0 
                reward += self._close_position_and_log(current_price, "TAKE_PROFIT")

        
        # --- Prepare for Next Step ---
        self.current_step += 1
        
        if not terminated and self.current_step < len(self.scaled_df):
            observation = self.scaled_df.iloc[self.current_step].values.astype(np.float32)
        else:
            observation = self.scaled_df.iloc[-1].values.astype(np.float32)

        info = self._get_info()
        truncated = False 
        
        # Update history
        self.net_worth_history.append(self.net_worth)
        self.drawdown_history.append(self.current_drawdown)
        self.reward_history.append(reward)
        
        return observation, reward, terminated, truncated, info