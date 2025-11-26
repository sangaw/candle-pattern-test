import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv

# ====================================================================
# A. The Trading Environment Class (Must be included)
# ====================================================================

class RiskRewardTradingEnv(gym.Env):
    """A custom environment for risk-reward constrained trading."""
    
    metadata = {'render_modes': ['human'], 'render_fps': 30}

    def __init__(self, df, rr_ratio=2.0, max_drawdown=0.10):
        super(RiskRewardTradingEnv, self).__init__()
        self.df = df.copy()
        self.rr_ratio = rr_ratio
        self.max_drawdown = max_drawdown
        self.initial_balance = 10000.0
        
        self.reset()

        # Action Space: 0: HOLD, 1: BUY/GO LONG, 2: CLOSE POSITION
        self.action_space = spaces.Discrete(3) 

        # Observation Space: [Close Price, RSI, SMA_50] - Scaled to a common range
        num_features = self.df.shape[1]
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(num_features,), dtype=np.float32
        )
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.balance = self.initial_balance
        self.net_worth = self.initial_balance
        self.max_net_worth = self.initial_balance
        self.shares_held = 0
        self.entry_price = 0
        self.current_step = 0
        self.history = []
        self.trade_count = 0
        self.current_drawdown = 0.0

        # Scale features using min/max of the entire dataset
        self.scaled_df = self._scale_data(self.df)
        
        # Get the first observation
        observation = self.scaled_df.iloc[self.current_step].values.astype(np.float32)
        info = self._get_info()
        return observation, info

    def _scale_data(self, df):
        """Simple min/max scaling for stability."""
        return (df - df.min()) / (df.max() - df.min())
    
    def _get_info(self):
        return {
            "net_worth": self.net_worth,
            "max_net_worth": self.max_net_worth,
            "shares_held": self.shares_held,
            "trade_count": self.trade_count,
            "drawdown": self.current_drawdown
        }

    def step(self, action):
        
        # Data for the current step (unscaled for calculations)
        current_data = self.df.iloc[self.current_step]
        current_price = current_data[self.df.columns[0]] # Assumes price is the first column
        
        # Default reward and termination
        reward = 0
        terminated = False
        
        # --- Handle Actions ---
        if action == 1: # BUY/GO LONG (Enter Position)
            if self.shares_held == 0:
                self.entry_price = current_price
                # Buy a fixed number of shares (or based on balance for simplicity)
                shares_to_buy = int(self.balance / current_price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    self.balance -= cost
                    self.shares_held = shares_to_buy
                    self.trade_count += 1
                    # Small negative reward for transaction cost or market impact
                    reward -= 0.01 
        
        elif action == 2: # CLOSE POSITION (Sell)
            if self.shares_held > 0:
                # Close the position
                sale_value = self.shares_held * current_price
                profit = sale_value - (self.shares_held * self.entry_price)
                self.balance += sale_value
                
                # Reward is the normalized profit
                reward += profit / self.initial_balance 
                
                # Reset position state
                self.shares_held = 0
                self.entry_price = 0
                
        # Update net worth and max net worth
        current_market_value = self.shares_held * current_price
        self.net_worth = self.balance + current_market_value
        self.max_net_worth = max(self.max_net_worth, self.net_worth)
        
        # Calculate current drawdown
        self.current_drawdown = (self.max_net_worth - self.net_worth) / self.max_net_worth
        
        # --- Check Termination Conditions ---
        if self.current_step == len(self.df) - 1:
            # End of all data
            terminated = True
        
        if self.shares_held > 0:
            # Check Stop Loss (Max Drawdown)
            if self.current_drawdown > self.max_drawdown:
                # Force close position at current price (stop loss hit)
                reward -= (self.max_drawdown * 10) # Heavy negative penalty
                self.balance += current_market_value
                self.shares_held = 0
                self.entry_price = 0
                terminated = True # End episode immediately after stop-out

            # Check Take Profit (R:R Ratio)
            price_change = (current_price - self.entry_price) / self.entry_price
            if price_change >= (self.max_drawdown * self.rr_ratio):
                # Force close position at current price (take profit hit)
                reward += (self.max_drawdown * self.rr_ratio * 10) # Heavy positive reward
                self.balance += current_market_value
                self.shares_held = 0
                self.entry_price = 0
                # Do NOT terminate, allow agent to continue trading
        
        # Increment step and prepare for next observation
        self.current_step += 1
        
        if not terminated:
            observation = self.scaled_df.iloc[self.current_step].values.astype(np.float32)
        else:
            # Return last observation if terminated
            observation = self.scaled_df.iloc[-1].values.astype(np.float32)

        info = self._get_info()

        # Truncated is always False for this fixed-length problem
        truncated = False 
        
        return observation, reward, terminated, truncated, info

# ====================================================================
# B. Main Execution: Data Loading, Training, and Backtesting
# ====================================================================

# --- 1. Data Collection & Feature Engineering (CSV Edition) ---
CSV_FILE_PATH = 'Nifty50_Historical_Data.csv' 
PRICE_COLUMN = 'Close' # Assumed column name for the closing price
INSTRUMENT_NAME = 'Nifty 50 Index'

print(f"Loading data for {INSTRUMENT_NAME} from {CSV_FILE_PATH}...")

try:
    # 1. Load data from CSV
    df = pd.read_csv(CSV_FILE_PATH)
    
    # 2. Clean and Index Data
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
    
    if PRICE_COLUMN not in df.columns:
        raise ValueError(f"CSV must contain a column named '{PRICE_COLUMN}' for the price.")

except FileNotFoundError:
    print(f"Error: CSV file not found at {CSV_FILE_PATH}. Please check the path and file name.")
    exit()
except ValueError as e:
    print(f"Data Error: {e}")
    exit()

# 3. Add simple technical indicators (Features for the State)
df['RSI'] = df[PRICE_COLUMN].diff().ewm(span=14).mean().fillna(0)
df['SMA_50'] = df[PRICE_COLUMN].rolling(window=50).mean()

# Drop initial NaNs created by rolling windows (e.g., first 50 rows for SMA)
df.dropna(inplace=True)

# Select features for the observation space
FEATURES = [PRICE_COLUMN, 'RSI', 'SMA_50']

# Create Train and Test splits
# Use the last 200 data points for testing
TRAIN_SPLIT = -200
train_df = df[FEATURES].iloc[:TRAIN_SPLIT]
test_df = df[FEATURES].iloc[TRAIN_SPLIT:]

print(f"Data split: Training on {len(train_df)} timesteps. Testing on {len(test_df)} timesteps.")


# --- 2. Environment Instantiation and Training ---
MODEL_PATH = "ddqn_nifty50_rr_model.zip"

train_env = make_vec_env(
    lambda: RiskRewardTradingEnv(train_df, rr_ratio=2.0, max_drawdown=0.10), 
    n_envs=1
)

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
    device='cpu' 
)

print("\nStarting DDQN training...")
model.learn(total_timesteps=100000) 
model.save(MODEL_PATH)
print("Training complete and model saved.")


# ====================================================================
# C. Backtesting on Test Data
# ====================================================================

print("\n--- Starting Backtest on Test Data ---")

# Load the trained model
loaded_model = DQN.load(MODEL_PATH, device='cpu')

# Create a test environment (non-vectorized for easy tracking)
# Set up a single environment for step-by-step backtesting
test_env_single = RiskRewardTradingEnv(test_df, rr_ratio=2.0, max_drawdown=0.10)
obs, info = test_env_single.reset()
done = False
current_step = 0
max_steps = len(test_df)

# Backtest loop
while not done:
    action, _ = loaded_model.predict(obs, deterministic=True) # deterministic=True for stable prediction
    obs, reward, terminated, truncated, info = test_env_single.step(action)
    done = terminated or truncated

# --- Print Results ---
initial_balance = test_env_single.initial_balance
final_net_worth = test_env_single.net_worth
total_return = (final_net_worth / initial_balance - 1) * 100
final_drawdown = test_env_single.current_drawdown
total_trades = test_env_single.trade_count

print("\n✅ Backtest Results:")
print("-" * 30)
print(f"Instrument: {INSTRUMENT_NAME}")
print(f"Test Period: {test_df.index[0].strftime('%Y-%m-%d')} to {test_df.index[-1].strftime('%Y-%m-%d')}")
print(f"Total Return: {total_return:.2f}%")
print(f"Final Net Worth: ${final_net_worth:,.2f}")
print(f"Maximum Drawdown (Target): 10.00%")
print(f"Actual Max Drawdown Observed: {final_drawdown*100:.2f}%")
print(f"Total Trades Executed: {total_trades}")

# ====================================================================