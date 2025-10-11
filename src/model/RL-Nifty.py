import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import gymnasium as gym
from gymnasium import spaces
from scipy.stats import norm
import random
from collections import deque

# --- 1. Black-Scholes Model Helper ---

class BlackScholesModel:
    """Calculates option price and Greeks (Delta, Gamma) for the environment state."""
    def __init__(self, K, r, sigma):
        self.K = K
        self.r = r
        self.sigma = sigma

    def _d1_d2(self, S, t, T):
        T_minus_t = T - t
        # Handle zero time to maturity to prevent division by zero/log(0)
        if T_minus_t <= 1e-6:
            return 0.0, 0.0
        
        d1 = (np.log(S / self.K) + (self.r + 0.5 * self.sigma**2) * T_minus_t) / (self.sigma * np.sqrt(T_minus_t))
        d2 = d1 - self.sigma * np.sqrt(T_minus_t)
        return d1, d2

    def price(self, S, t, T):
        T_minus_t = T - t
        if T_minus_t <= 1e-6:
            return np.maximum(S - self.K, 0)
        d1, d2 = self._d1_d2(S, t, T)
        N_d1 = norm.cdf(d1)
        N_d2 = norm.cdf(d2)
        return S * N_d1 - self.K * np.exp(-self.r * T_minus_t) * N_d2

    def delta(self, S, t, T):
        T_minus_t = T - t
        if T_minus_t <= 1e-6:
            return 1.0 if S > self.K else 0.0
        d1, _ = self._d1_d2(S, t, T)
        return norm.cdf(d1)

    def gamma(self, S, t, T):
        T_minus_t = T - t
        if T_minus_t <= 1e-6:
            return 0.0 
        d1, _ = self._d1_d2(S, t, T)
        return norm.pdf(d1) / (S * self.sigma * np.sqrt(T_minus_t))

# --- 2. NIFTY Option Trading Environment (Gymnasium) ---

# Global NIFTY Option Parameters
K_STRIKE = 25000.0
R_RATE = 0.055
SIGMA = 0.15
T_MATURITY = 0.5 # 6 months to maturity

class NiftyOptionTradingEnv(gym.Env):
    """
    Gymnasium environment for a short NIFTY CE option trading strategy.
    
    Actions: 0: Hold, 1: Sell (Entry), 2: Cover (Exit)
    State: [S, Time_Left, Delta, Gamma, Position]
    Reward: P&L change - Transaction Cost - Risk Penalty
    """
    def __init__(self, start_S=24500, max_steps=126):
        super(NiftyOptionTradingEnv, self).__init__()
        
        self.model = BlackScholesModel(K_STRIKE, R_RATE, SIGMA)
        self.start_S = start_S
        self.max_steps = max_steps 

        # Define Action and State Space
        self.action_space = spaces.Discrete(3) 
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, -1], dtype=np.float32), 
            high=np.array([50000, T_MATURITY, 1, 1, 0], dtype=np.float32)) 
        
        # Strategy/Cost Parameters (Tunable)
        self.TRANSACTION_COST = 5.0 
        self.RISK_GAMMA_WEIGHT = 5000.0  # Penalize high Gamma risk
        self.RISK_DELTA_WEIGHT = 20.0    # Penalize large directional risk (Delta)
        
        self.reset()

    def _get_obs(self):
        time_left = T_MATURITY - self.t
        C = self.model.price(self.S, self.t, T_MATURITY)
        delta = self.model.delta(self.S, self.t, T_MATURITY)
        gamma = self.model.gamma(self.S, self.t, T_MATURITY)
        
        # Normalize Gamma for better NN training
        # Max Gamma for K=25000, T=0.5, sigma=0.15 is about 0.00018
        gamma_norm = np.clip(gamma * 10000, 0, 1) 
        
        return np.array([self.S, time_left, delta, gamma_norm, self.current_position], dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.S = self.start_S
        self.t = 0.0
        self.current_position = 0 
        self.entry_price = 0.0
        self.steps_taken = 0
        self.pnl = 0.0
        
        return self._get_obs(), {}

    def step(self, action):
        
        prev_C = self.model.price(self.S, self.t, T_MATURITY)
        reward = 0.0
        transaction_made = False
        
        # 1. Process Action (A)
        if action == 1 and self.current_position == 0: # SELL (Entry)
            self.current_position = -1
            self.entry_price = prev_C 
            reward -= self.TRANSACTION_COST
            transaction_made = True
            
        elif action == 2 and self.current_position == -1: # COVER (Exit)
            current_C = prev_C 
            pnl_realized = (self.entry_price - current_C) - self.TRANSACTION_COST
            reward += pnl_realized
            self.pnl += pnl_realized
            self.current_position = 0 
            transaction_made = True
            
        # 2. Simulate Market Movement
        dt = T_MATURITY / self.max_steps
        self.t += dt
        self.steps_taken += 1
        
        # GBM simulation
        dW = np.random.normal(0, np.sqrt(dt))
        self.S = self.S * np.exp((R_RATE - 0.5 * SIGMA**2) * dt + SIGMA * dW)
        
        # 3. Calculate Risk-Adjusted Reward (R)
        
        # Unrealized P&L Update (for holding positions)
        current_C = self.model.price(self.S, self.t, T_MATURITY)
        if self.current_position == -1 and not transaction_made:
            unrealized_pnl_change = (self.entry_price - current_C) - (self.entry_price - prev_C)
            reward += unrealized_pnl_change
        
        # RISK PENALTY (Core of the strategy)
        if self.current_position == -1:
            current_delta = self.model.delta(self.S, self.t, T_MATURITY)
            current_gamma = self.model.gamma(self.S, self.t, T_MATURITY)
            
            risk_penalty = (self.RISK_DELTA_WEIGHT * np.abs(current_delta) + 
                            self.RISK_GAMMA_WEIGHT * current_gamma)
            
            reward -= risk_penalty 
            
        # 4. Check Termination
        terminated = self.steps_taken >= self.max_steps
        
        # Finalize P&L if position is still open at expiry
        if terminated and self.current_position == -1:
            final_value = np.maximum(self.S - K_STRIKE, 0)
            final_pnl = (self.entry_price - final_value)
            reward += final_pnl # Add final P&L to the reward
            self.pnl += final_pnl
        
        return self._get_obs(), reward, terminated, False, {}


# --- 3. Deep Q-Network (DQN) Agent ---

# Hyperparameters
GAMMA = 0.99            # Discount factor for future rewards
LEARNING_RATE = 0.001   # Model learning rate
MEMORY_SIZE = 10000     # Maximum experience replay capacity
BATCH_SIZE = 64         # Batch size for training
EXPLORATION_MAX = 1.0   # Initial exploration rate (epsilon)
EXPLORATION_MIN = 0.01  # Minimum exploration rate
EXPLORATION_DECAY = 0.995 # Decay rate per episode

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=MEMORY_SIZE)
        self.gamma = GAMMA
        self.epsilon = EXPLORATION_MAX
        self.epsilon_min = EXPLORATION_MIN
        self.epsilon_decay = EXPLORATION_DECAY
        
        # Device setup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Neural Network for Q-function
        self.model = self._build_model().to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=LEARNING_RATE)
        self.criterion = nn.MSELoss()

    def _build_model(self):
        # A simple Feedforward network (DQN)
        model = nn.Sequential(
            nn.Linear(self.state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, self.action_size)
        )
        return model

    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory."""
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        """Epsilon-greedy action selection."""
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size) # Explore
        
        # Exploit: Choose action with max Q-value
        state_tensor = torch.FloatTensor(state).to(self.device)
        with torch.no_grad():
            q_values = self.model(state_tensor)
        return torch.argmax(q_values).item()

    def replay(self):
        """Train the model using experiences sampled from the memory."""
        if len(self.memory) < BATCH_SIZE:
            return

        minibatch = random.sample(self.memory, BATCH_SIZE)
        
        # Convert batch to tensors
        states = torch.FloatTensor(np.array([t[0] for t in minibatch])).to(self.device)
        actions = torch.LongTensor(np.array([t[1] for t in minibatch])).to(self.device)
        rewards = torch.FloatTensor(np.array([t[2] for t in minibatch])).to(self.device)
        next_states = torch.FloatTensor(np.array([t[3] for t in minibatch])).to(self.device)
        dones = torch.FloatTensor(np.array([t[4] for t in minibatch])).to(self.device)

        # Compute Q(s_t, a) - the predicted Q-value for the action taken
        current_q_values = self.model(states).gather(1, actions.unsqueeze(1)).squeeze(1)

        # Compute V(s_{t+1}) = max_a' Q(s_{t+1}, a')
        next_q_values = self.model(next_states).max(1)[0]
        
        # Compute target Q-value: R + gamma * V(s_{t+1})
        # If the episode is done (dones=1), the target Q-value is just R
        target_q_values = rewards + self.gamma * next_q_values * (1 - dones)
        
        # Backpropagation
        loss = self.criterion(current_q_values, target_q_values.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Decay Epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# --- 4. Main Training Function ---

def train_rl_agent(num_episodes=5000):
    env = NiftyOptionTradingEnv()
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    agent = DQNAgent(state_size, action_size)
    
    print(f"Starting DQN Training for NIFTY Option Strategy on {agent.device}...")
    print(f"Goal: Maximize Risk-Adjusted P&L (Penalty for high Delta/Gamma)")
    
    # Store P&L for plotting/analysis later
    episode_pnls = [] 
    
    for episode in range(1, num_episodes + 1):
        state, _ = env.reset()
        terminated = False
        total_pnl = 0.0
        
        while not terminated:
            action = agent.act(state)
            next_state, reward, terminated, truncated, info = env.step(action)
            agent.remember(state, action, reward, next_state, terminated)
            state = next_state
            
            # Simple check to ensure enough data for replay before starting
            if len(agent.memory) > BATCH_SIZE:
                agent.replay()
                
            total_pnl = env.pnl 
        
        episode_pnls.append(total_pnl)
        
        if episode % 100 == 0:
            avg_pnl = np.mean(episode_pnls[-100:])
            print(f"Episode {episode}/{num_episodes} | Avg. 100-Ep P&L: Rs. {avg_pnl:.2f} | Epsilon: {agent.epsilon:.4f}")
            
    print("\nTraining Finished.")
    
    # --- Optional: Basic Evaluation/Visualization ---
    
    # Simple Plot of P&L over time to see convergence
    if len(episode_pnls) > 0:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12, 6))
        plt.plot(episode_pnls, label='Episode Final P&L')
        
        # Calculate a rolling average for smoothing
        rolling_avg = np.convolve(episode_pnls, np.ones(50)/50, mode='valid')
        plt.plot(np.arange(len(rolling_avg)) + 50, rolling_avg, color='red', label='50-Episode Rolling Avg P&L', linewidth=2)
        
        plt.title('RL Agent Performance: NIFTY Option Strategy')
        plt.xlabel('Episode')
        plt.ylabel('Final P&L (Rs.)')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == '__main__':
    train_rl_agent(num_episodes=5000)