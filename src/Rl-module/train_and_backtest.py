import numpy as np
import pandas as pd
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from sklearn.preprocessing import MinMaxScaler
import warnings

# Suppress FutureWarning from pandas in the environment
warnings.filterwarnings("ignore", category=FutureWarning)


# --- IMPORTANT: Import the Environment Class ---
from trading_env import RiskRewardTradingEnv 

# ====================================================================
# HELPER FUNCTIONS FOR PERFORMANCE METRICS
# ====================================================================

def calculate_sharpe(net_worth_history, risk_free_rate=0.0):
    """Calculates the annualized Sharpe Ratio."""
    if len(net_worth_history) < 2:
        return 0.0
    
    # Calculate daily returns
    returns = pd.Series(net_worth_history).pct_change().dropna()
    
    # Annualized Sharpe Ratio (assuming daily data, 252 trading days/year)
    annualized_return = returns.mean() * 252
    annualized_std = returns.std() * np.sqrt(252)
    
    if annualized_std == 0:
        return np.inf if annualized_return > 0 else 0.0
        
    # Risk-free rate is often assumed to be 0 for simplicity in RL backtests
    return (annualized_return - risk_free_rate) / annualized_std

def calculate_mdd(net_worth_history):
    """Calculates the maximum drawdown from net worth history."""
    if not net_worth_history:
        return 0.0
    
    peak = net_worth_history[0]
    max_dd = 0.0
    for current_net_worth in net_worth_history:
        peak = max(peak, current_net_worth)
        drawdown = (peak - current_net_worth) / peak
        max_dd = max(max_dd, drawdown)
    return max_dd

# ====================================================================
# A. Configuration and Data Loading
# ====================================================================
CSV_FILE_PATH ="C:\\Users\\Sandeep\\Documents\\Work\\code\\candle-pattern-test\\data\\nifty\\train\\full_featured.csv"
PRICE_COLUMN = 'close' 
INSTRUMENT_NAME = 'Nifty 50 Index'
MODEL_PATH = "ddqn_nifty50_rr_model.zip"
LOG_DIR = "./ddqn_tensorboard/" # Path for TensorBoard logs (optional, but good practice)
                
print(f"Loading data for {INSTRUMENT_NAME} from {CSV_FILE_PATH}...")

# Load and clean data (assuming 'date' and 'close' columns exist)
try:
    df = pd.read_csv(CSV_FILE_PATH)
    if 'date' in df.columns:
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

# Select features for the observation space
# CRITICAL: PRICE_COLUMN is placed first but is NOT scaled.
FEATURES = [PRICE_COLUMN, 'RSI', 'SMA_50']
INDICATORS = ['RSI', 'SMA_50'] # Only indicators will be scaled.

# Define the split point: last 120 days for testing
TRAIN_SPLIT = -120 

# ------------------------------------------------------------------------
# --- 1. Fit the Scaler on the Training Data ONLY (Crucial Step) ---
# ------------------------------------------------------------------------

# Select ALL rows *before* the index -120 for indicators only.
train_indicators = df[INDICATORS].iloc[:TRAIN_SPLIT] 

# Initialize and fit the scaler using the training data's indicators only
scaler = MinMaxScaler()
scaler.fit(train_indicators.values) 

# ------------------------------------------------------------------------
# --- 2. Apply the Transformation to ONLY Indicator Data ---
# ------------------------------------------------------------------------

# Apply the transformation (using training stats) to the full indicators dataset
df_normalized_indicators = pd.DataFrame(
    scaler.transform(df[INDICATORS].values), 
    columns=INDICATORS, 
    index=df.index
)

# Replace the original indicator features in the main DataFrame with the normalized ones
# NOTE: PRICE_COLUMN remains unscaled.
df[INDICATORS] = df_normalized_indicators[INDICATORS]

# ------------------------------------------------------------------------
# --- 3. Final Train/Test Split ---
# ------------------------------------------------------------------------

train_df = df[FEATURES].iloc[:TRAIN_SPLIT] 
test_df = df[FEATURES].iloc[TRAIN_SPLIT:]

print(f"Data loaded. Training on {len(train_df)} timesteps. Testing on {len(test_df)} timesteps.")


def train_ddqn(train_df):
    """Train a DDQN (SB3 DQN) agent and save the model to disk."""
    print("\n--- Starting DDQN Training ---")

    # Instantiate the training environment (Vectorized for SB3)
    train_env = make_vec_env(
        lambda: RiskRewardTradingEnv(train_df, rr_ratio=2.0, max_drawdown=0.10), 
        n_envs=1
    )

    # Double-DQN specific policy kwargs
    ddqn_policy_kwargs = dict(
        net_arch=[256, 256],
    )

    ddqn_model = DQN(
        "MlpPolicy",
        train_env, 
        learning_rate=2.5e-4,
        buffer_size=200000,
        learning_starts=2000,
        batch_size=128,
        gamma=0.99,
        tau=1.0,
        train_freq=4,
        gradient_steps=1,
        target_update_interval=500,
        exploration_fraction=0.2,
        exploration_initial_eps=1.0,
        exploration_final_eps=0.02, # Set to 0.02 for the final exploration rate
        policy_kwargs=ddqn_policy_kwargs,
        verbose=0,
        device='cpu',
        tensorboard_log=LOG_DIR # Enable TensorBoard logging for training visualization
    )

    ddqn_model.learn(total_timesteps=400000) 
    ddqn_model.save(MODEL_PATH)
    print("Training complete and model saved.")


def backtest_ddqn(test_df):
    """Run backtest using a saved DDQN model and print performance metrics."""
    print("\n--- Starting Backtest on Unseen Test Data ---")

    # Load the trained DDQN model
    loaded_model = DQN.load(MODEL_PATH, device='cpu')

    # Create a single test environment for step-by-step backtesting
    test_env_single = RiskRewardTradingEnv(test_df, rr_ratio=2.0, max_drawdown=0.10)
    obs, info = test_env_single.reset()
    done = False

    # Backtest loop
    while not done:
        action, _ = loaded_model.predict(obs, deterministic=True) 
        scalar_action = action.item()
        obs, reward, terminated, truncated, info = test_env_single.step(scalar_action)
        done = terminated or truncated

    # --- Calculate and Print Final Results (Business KPIs) ---
    initial_balance = test_env_single.initial_balance
    final_net_worth = test_env_single.net_worth
    total_return = (final_net_worth / initial_balance - 1) * 100
    total_trades = test_env_single.trade_count

    # Calculate Max Drawdown and Sharpe Ratio using the full net worth history
    mdd_observed = calculate_mdd(test_env_single.net_worth_history)
    sharpe_ratio = calculate_sharpe(test_env_single.net_worth_history)

    print("\n✅ Final Backtest Performance Metrics:")
    print("-" * 50)
    print(f"Instrument: {INSTRUMENT_NAME}")
    print(f"Test Period Length: {len(test_df)} days")
    print(f"Total Trades Executed: {total_trades}")
    print(f"Final Net Worth: ${final_net_worth:,.2f}")
    print(f"Total Return: {total_return:.2f}%") 
    print(f"**Annualized Sharpe Ratio:** {sharpe_ratio:.2f}")
    print(f"Max Drawdown Policy Limit: {test_env_single.max_drawdown*100:.2f}%")
    print(f"**Actual Max Drawdown Observed:** {mdd_observed*100:.2f}%")
    print("-" * 50)

    # --- Generate Trade Log for Evaluation ---
    trades_df = pd.DataFrame(test_env_single.trades_log)

    if not trades_df.empty:
        print("\n🔍 Trade-by-Trade Log Summary (First 10 Trades):")
        # Display key columns of the trade log for policy analysis
        print(trades_df[['entry_step', 'exit_step', 'duration', 'outcome', 'profit_pct', 'shares']].head(10).to_markdown(index=False, numalign="left", stralign="left"))
        print(f"\n... Showing first 10 of {len(trades_df)} trades.")
    else:
        print("\n⚠️ No trades were executed by the agent in the test period. This may indicate an overly cautious policy or a failure to identify entry points.")


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Train and/or backtest DDQN trading agent.")
    parser.add_argument(
        "--mode",
        choices=["train", "test", "both"],
        default="both",
        help="What to run: 'train' (only train), 'test' (only test using saved model), or 'both' (default).",
    )
    args = parser.parse_args()

    # Safety check when user asks for test-only
    if args.mode in ("test", "both") and not os.path.exists(MODEL_PATH):
        print(f"Model file '{MODEL_PATH}' not found. You must train first (use --mode train or both).")
        raise SystemExit(1)

    if args.mode in ("train", "both"):
        train_ddqn(train_df)

    if args.mode in ("test", "both"):
        backtest_ddqn(test_df)