import numpy as np
import pandas as pd
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from sklearn.preprocessing import MinMaxScaler


# --- IMPORTANT: Import the Environment Class ---
# This line requires trading_env.py to be in the same folder.
from trading_env import RiskRewardTradingEnv 

# ====================================================================
# A. Configuration and Data Loading
# ====================================================================
# CSV_FILE_PATH = 'Nifty50_Historical_Data.csv' 
CSV_FILE_PATH ="C:\\Users\\Sandeep\\Documents\\Work\\code\\candle-pattern-test\\data\\nifty\\train\\full_featured.csv"
PRICE_COLUMN = 'close' # Check your CSV for the correct column name!
INSTRUMENT_NAME = 'Nifty 50 Index'
MODEL_PATH = "ddqn_nifty50_rr_model.zip"
                
print(f"Loading data for {INSTRUMENT_NAME} from {CSV_FILE_PATH}...")

try:
    df = pd.read_csv(CSV_FILE_PATH)
    
    # Clean and Index Data
    if 'date' in df.columns:
        print(f"Found date column")
        df['Date'] = pd.to_datetime(df['date'])
        df.set_index('Date', inplace=True)
    
    if PRICE_COLUMN not in df.columns:
        raise ValueError(f"CSV must contain a column named '{PRICE_COLUMN}' for the price.")

except FileNotFoundError:
    print(f"Error: CSV file not found at {CSV_FILE_PATH}. Please check the path.")
    exit()
except ValueError as e:
    print(f"Data Error: {e}")
    exit()

# Add simple technical indicators (Features for the State)
df['RSI'] = df[PRICE_COLUMN].diff().ewm(span=14).mean().fillna(0)
df['SMA_50'] = df[PRICE_COLUMN].rolling(window=50).mean()

df.dropna(inplace=True)

# Select features for the observation space (Order matters! Price must be first)
FEATURES = [PRICE_COLUMN, 'RSI', 'SMA_50']

# date,open,high,low,close, ,daily_return,log_return,price_range,ma_5,ma_20,volatility_5,volatility_20,rsi_14,macd_12_26,macd_signal_12_26,macd_histogram_12_26,
# macd_signal_strength,stoch_14,stoch_smoothk,stoch_smoothd,dow_trend_spec_raw,dow_trend_spec,range,avg_range,is_mother_candle,mother_candle_trend,
# final_trend,trend_code

# Define the features selected from the heatmap analysis
# FEATURES = [PRICE_COLUMN, 'RSI', 'SMA_50', 'rsi_14', 'ma_20', 'macd_12_26', 'stoch_14','trend_code', 'price_range']

# Define the split point: last 120 days for testing
TRAIN_SPLIT = -120 # Represents the index of the first test row

# ------------------------------------------------------------------------
# --- 1. Fit the Scaler on the Training Data ONLY (Crucial Step) ---
# ------------------------------------------------------------------------

# Select ALL rows *before* the index -120. This is the correct training set.
# The slice [ : TRAIN_SPLIT ] ensures we avoid the last 120 rows.
train_data = df[FEATURES].iloc[:TRAIN_SPLIT] 

# Initialize the scaler
scaler = MinMaxScaler()

# Fit the scaler using the training data's statistics only
# train_data is now a DataFrame, so we use .values
scaler.fit(train_data.values) 

# ------------------------------------------------------------------------
# --- 2. Apply the Transformation to ALL Data ---
# ------------------------------------------------------------------------

# Create a new DataFrame for the normalized features
df_normalized = pd.DataFrame(
    # Apply the transformation (using training stats) to the full dataset (df[FEATURES].values)
    scaler.transform(df[FEATURES].values), 
    columns=FEATURES, 
    index=df.index
)

# Replace the original features in the main DataFrame with the normalized ones
# df[FEATURES] = df_normalized[FEATURES]

# ------------------------------------------------------------------------
# --- 3. Final Train/Test Split ---
# ------------------------------------------------------------------------

# Slice the now-normalized df into the final training set
train_df = df[FEATURES].iloc[:TRAIN_SPLIT] 

# Slice the now-normalized df into the final test set
test_df = df[FEATURES].iloc[TRAIN_SPLIT:]

# Confirmation (optional)
print(f"Total dataset size: {len(df)}")
print(f"Training set size: {len(train_df)}")
print(f"Test set size: {len(test_df)}")

print(f"Data loaded. Training on {len(train_df)} timesteps. Testing on {len(test_df)} timesteps.")


# ====================================================================
# B. DDQN Training (CPU Optimized)
# ====================================================================
print("\n--- Starting DDQN Training ---")

# Commented as scaler object is passed Instantiate the training environment (Vectorized for SB3)
train_env = make_vec_env(
    lambda: RiskRewardTradingEnv(train_df, rr_ratio=2.0, max_drawdown=0.10), 
    n_envs=1
)


# train_env = make_vec_env(
#    lambda: RiskRewardTradingEnv(train_df, scaler=scaler), 
#    n_envs=1
#)


model = DQN(
    "MlpPolicy",
    train_env, 
    learning_rate=5e-4,
    buffer_size=100000,     # Experience Replay Buffer (uses RAM)
    learning_starts=1000,
    gamma=0.99,
    exploration_fraction=0.5,
    verbose=0,
    device='cpu'            # Explicitly use the CPU
)

model.learn(total_timesteps=1000000) 
model.save(MODEL_PATH)
print("Training complete and model saved.")


# ====================================================================
# C. Backtesting on Test Data
# ====================================================================

print("\n--- Starting Backtest on Unseen Test Data ---")

# Load the trained model
loaded_model = DQN.load(MODEL_PATH, device='cpu')

# Create a single test environment for step-by-step backtesting
test_env_single = RiskRewardTradingEnv(test_df, rr_ratio=2.0, max_drawdown=0.10)
obs, info = test_env_single.reset()
done = False

# Backtest loop
while not done:
    # Use deterministic=True to get the learned (non-exploratory) best action
    action, _ = loaded_model.predict(obs, deterministic=True) 
    
    # --- Safely extract the scalar action ---
    scalar_action = action.item()
    
    obs, reward, terminated, truncated, info = test_env_single.step(scalar_action)
    done = terminated or truncated

# --- Print Final Results ---
initial_balance = test_env_single.initial_balance
final_net_worth = test_env_single.net_worth
total_return = (final_net_worth / initial_balance - 1) * 100
final_drawdown = test_env_single.current_drawdown
total_trades = test_env_single.trade_count

print("\n✅ Final Backtest Results:")
print("-" * 40)
print(f"Instrument: {INSTRUMENT_NAME}")
print(f"Test Period Length: {len(test_df)} days")
print(f"Total Trades Executed: {total_trades}")
print(f"Total Return: {total_return:.2f}%") 
print(f"Final Net Worth: ${final_net_worth:,.2f}")
print(f"Max Drawdown Constraint: 10.00%")
print(f"Actual Max Drawdown Observed: {final_drawdown*100:.2f}%")
print("-" * 40)