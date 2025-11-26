import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env

# The RiskRewardTradingEnv class from the previous response goes here
# (It remains unchanged)
# ...
# [RiskRewardTradingEnv Class code goes here - truncated for brevity]
# ...

import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces

class RiskRewardTradingEnv(gym.Env):
    # Standard Gymnasium setup
    metadata = {'render_modes': ['human'], 'render_fps': 3}

    def __init__(self, df, initial_balance=10000, rr_ratio=2.0, max_drawdown=0.10):
        super().__init__()
        self.df = df
        self.initial_balance = initial_balance
        self.rr_ratio = rr_ratio # Example: 2.0 (2:1 Risk-Reward)
        self.max_drawdown = max_drawdown # Max risk tolerance (10% loss)

        # 1. Action Space: Discrete for Buy, Sell, Hold (DDQN requirement)
        self.action_space = spaces.Discrete(3) # 0: Sell/Close, 1: Buy/Open, 2: Hold

        # 2. Observation Space (State): Includes price and indicators
        # Example features: [Price, RSI, MACD, Portfolio Value, Current Position Status]
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(df.shape[1] + 2,), dtype=np.float32
        )

        # State tracking variables
        self._reset()


    # --- CORE RL METHODS ---

    def _reset(self, seed=None, options=None):
        super()._reset(seed=seed)
        self.current_step = 0
        self.balance = self.initial_balance
        self.shares_held = 0
        self.net_worth = self.initial_balance
        self.max_net_worth = self.initial_balance
        self.entry_price = 0.0 # Price when the position was opened
        self.position = 0 # 0: None, 1: Long
        self.trade_profit_target = 0.0 # Target profit for current trade
        self.trade_stop_loss = 0.0 # Stop loss for current trade

        observation = self._get_observation()
        info = self._get_info()
        return observation, info


    def _get_observation(self):
        # Current data row (price, indicators)
        features = self.df.iloc[self.current_step].values

        # Add current portfolio state
        portfolio_state = np.array([
            self.net_worth,
            self.position
        ])
        return np.concatenate((features, portfolio_state))


    def _get_info(self):
        return {
            'net_worth': self.net_worth,
            'balance': self.balance,
            'shares': self.shares_held
        }


    def step(self, action):
        # Move to the next timestep
        self.current_step += 1
        current_price = self.df['Close'].iloc[self.current_step]
        reward = 0
        terminated = False
        truncated = False

        # --- A. RR Condition Logic ---
        if self.position == 1: # We are currently in a LONG trade
            pnl = (current_price - self.entry_price) * self.shares_held

            # 1. Check Take Profit (Risk-Reward Achieved)
            if current_price >= self.trade_profit_target:
                reward += self._close_position(current_price, 'TP')
                # A large positive reward for achieving the target
                reward += 10.0 * self.rr_ratio 
                print(f"TP Hit! Reward: {reward}")

            # 2. Check Stop Loss (Risk Breached)
            elif current_price <= self.trade_stop_loss:
                reward += self._close_position(current_price, 'SL')
                # A large negative penalty for breaching risk limit
                reward -= 10.0 
                print(f"SL Hit! Penalty: {reward}")

            # 3. If action is Sell/Close (0), manually close
            elif action == 0:
                reward += self._close_position(current_price, 'Manual')
                # Small penalty/reward for early exit, depending on PnL
                reward += pnl / self.initial_balance * 5.0
                
            # 4. If action is Hold (2), no transaction, small time reward/penalty
            elif action == 2:
                reward += pnl / self.initial_balance * 0.1 # Small reward for successful holding


        # --- B. Action Execution ---
        if action == 1 and self.position == 0: # Buy/Open
            # Use a simple fixed position for this example
            self._open_position(current_price)
            # No immediate reward, the next steps determine the outcome

        # Update net worth and check for termination
        self.net_worth = self.balance + self.shares_held * current_price
        self.max_net_worth = max(self.max_net_worth, self.net_worth)
        drawdown = (self.max_net_worth - self.net_worth) / self.max_net_worth

        # Termination condition: Max Drawdown breached OR End of Data
        if drawdown > self.max_drawdown or self.current_step >= len(self.df) - 1:
            terminated = True
            # Penalize end-of-episode position (unless it's profitable)
            if self.position == 1:
                reward += self._close_position(current_price, 'End') / self.initial_balance * 5.0
            
            # Heavy penalty if max drawdown is hit
            if drawdown > self.max_drawdown:
                reward -= 50.0

        # Update observation and return
        observation = self._get_observation()
        info = self._get_info()
        return observation, reward, terminated, truncated, info


    # --- HELPER METHODS FOR TRADES ---

    def _open_position(self, current_price):
        # 1. Determine shares to buy (e.g., use 50% of current balance)
        investment_amount = self.balance * 0.5 
        shares = int(investment_amount / current_price)

        if shares > 0:
            self.shares_held = shares
            cost = shares * current_price
            self.balance -= cost
            self.position = 1
            self.entry_price = current_price

            # 2. **Calculate SL and TP based on RR condition (The key step!)**
            # Define fixed risk (e.g., 2% of the trade value)
            risk_percent = 0.02 
            risk_value = self.entry_price * risk_percent
            
            self.trade_stop_loss = self.entry_price - risk_value
            # TP = Entry + (Risk * RR_Ratio)
            self.trade_profit_target = self.entry_price + (risk_value * self.rr_ratio)


    def _close_position(self, current_price, reason):
        if self.position == 1:
            profit = (current_price - self.entry_price) * self.shares_held
            self.balance += self.shares_held * current_price
            self.shares_held = 0
            self.position = 0
            
            # Reset RR targets
            self.entry_price = 0.0
            self.trade_profit_target = 0.0
            self.trade_stop_loss = 0.0
            
            # Reward: Profit as a percentage of the initial balance
            return profit / self.initial_balance
        return 0.0


# --- 1. Data Collection & Feature Engineering (CSV Edition) ---
CSV_FILE_PATH = 'Nifty50_Historical_Data.csv' 
PRICE_COLUMN = 'Close' # The column name for the closing price in your CSV

try:
    # 1. Load data from CSV
    df = pd.read_csv(CSV_FILE_PATH)
    
    # 2. Clean and Index Data
    # Assume the date column is named 'Date' (common for Nifty data)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
    
    # Ensure the required column exists
    if PRICE_COLUMN not in df.columns:
        raise ValueError(f"CSV must contain a column named '{PRICE_COLUMN}' for the price.")

except FileNotFoundError:
    print(f"Error: CSV file not found at {CSV_FILE_PATH}. Please check the path.")
    exit()
except ValueError as e:
    print(f"Data Error: {e}")
    exit()

# 3. Add simple technical indicators (Features for the State)
# We calculate RSI and SMA based on the Nifty 50 'Close' price
df['RSI'] = df[PRICE_COLUMN].diff().ewm(span=14).mean().fillna(0)
df['SMA_50'] = df[PRICE_COLUMN].rolling(window=50).mean()

# Drop initial NaNs created by rolling windows (e.g., first 50 rows for SMA)
df.dropna(inplace=True)

# Select features for the observation space
# Note: 'Close' must be included as the environment needs the price.
FEATURES = [PRICE_COLUMN, 'RSI', 'SMA_50']

# Create Train and Test splits
# We use the last 200 data points for testing
train_df = df[FEATURES].iloc[:-200]
test_df = df[FEATURES].iloc[-200:]

print(f"Nifty 50 Data Loaded. Training on {len(train_df)} timesteps.")


# --- 2. Environment Instantiation ---
# The lambda function creates a fresh environment for each vector
train_env = make_vec_env(
    lambda: RiskRewardTradingEnv(train_df, rr_ratio=2.0, max_drawdown=0.10), 
    n_envs=1
)


# --- 3. DDQN (DQN in SB3) Agent Setup and Training ---
model = DQN(
    "MlpPolicy",
    train_env,
    learning_rate=1e-4,
    buffer_size=100000,
    learning_starts=1000,
    batch_size=32,
    gamma=0.99,
    target_update_interval=1000,
    exploration_fraction=0.1,
    verbose=0,
    device='cpu'            # Confirms CPU usage for your hardware
)

print("Starting DDQN training on Nifty 50 (CPU)...")
# Reduced total_timesteps for faster demo/CPU constraint
model.learn(total_timesteps=100000) 
model.save("ddqn_nifty50_rr_model")
print("Training complete and model saved.")


