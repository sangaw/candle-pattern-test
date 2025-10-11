import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from torch.autograd import grad
from scipy.stats import norm

# --- 1. Black-Scholes Parameters and Domain ---
# European Call Option Parameters
K = 100.0   # Strike Price
r = 0.05    # Risk-free rate
sigma = 0.2 # Volatility
T = 1.0     # Time to maturity (years)

# Computational Domain for (S, t)
S_min = 50.0
S_max = 150.0
t_min = 0.0
t_max = T

# Training Hyperparameters
N_COL = 10000  # Number of collocation points (PDE domain)
N_IC = 1000    # Number of initial condition points (t=T)
N_BC = 1000    # Number of boundary condition points (S=S_min and S=S_max)
N_EPOCHS = 20000
LEARNING_RATE = 1e-3
WEIGHTS = {'pde': 1.0, 'ic': 100.0, 'bc': 100.0} # Loss weights

# --- 2. Black-Scholes Analytical Solution (for IC/BC and validation) ---
# Function to calculate the Black-Scholes Call Price
def black_scholes_call(S, K, T, r, sigma):
    d1 = (torch.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * torch.sqrt(T))
    d2 = d1 - sigma * torch.sqrt(T)
    call_price = S * norm.cdf(d1.detach().cpu().numpy()) - K * torch.exp(-r * T) * norm.cdf(d2.detach().cpu().numpy())
    return torch.tensor(call_price, dtype=torch.float32).to(S.device)

# Initial Condition (at t=T) is the option's payoff
def initial_condition(S, K):
    return torch.relu(S - K)

# Boundary Condition (for S_min=0) - Value is 0 as S->0
# Note: For S_max large, C -> S
def boundary_condition_low(t, K, r):
    # For a European Call with S->0, C -> 0
    return torch.zeros_like(t) 

def boundary_condition_high(S, t, K, r):
    # For a European Call with S->infinity, C -> S - K*exp(-r*(T-t))
    time_to_maturity = T - t
    return S - K * torch.exp(-r * time_to_maturity)

# --- 3. PINN Model Definition ---
class PINN(nn.Module):
    def __init__(self):
        super(PINN, self).__init__()
        # Input: (S, t) -> Output: C(S, t)
        self.net = nn.Sequential(
            nn.Linear(2, 50), nn.Tanh(),
            nn.Linear(50, 50), nn.Tanh(),
            nn.Linear(50, 50), nn.Tanh(),
            nn.Linear(50, 1)
        )
        # Initialize weights
        nn.init.xavier_uniform_(self.net[0].weight)

    def forward(self, x):
        return self.net(x)

# --- 4. Loss Function (The "Physics-Informed" part) ---
def pde_loss(model, S_t_col, K, r, sigma):
    # Ensure inputs require gradient for automatic differentiation
    S = S_t_col[:, 0].unsqueeze(1).requires_grad_(True)
    t = S_t_col[:, 1].unsqueeze(1).requires_grad_(True)
    
    # Model prediction: C(S, t)
    C = model(torch.cat([S, t], dim=1))
    
    # Compute first-order derivatives
    # dC/dS
    dC_dS = grad(C, S, grad_outputs=torch.ones_like(C), create_graph=True)[0]
    # dC/dt
    dC_dt = grad(C, t, grad_outputs=torch.ones_like(C), create_graph=True)[0]
    
    # Compute second-order derivative: d^2C/dS^2
    d2C_dS2 = grad(dC_dS, S, grad_outputs=torch.ones_like(dC_dS), create_graph=True)[0]
    
    # Black-Scholes PDE Residual:
    # dC/dt + 0.5 * sigma^2 * S^2 * d^2C/dS^2 + r * S * dC/dS - r * C = 0
    pde_res = dC_dt + 0.5 * sigma**2 * S**2 * d2C_dS2 + r * S * dC_dS - r * C
    
    # The PDE loss is the Mean Squared Error of the residual
    return torch.mean(pde_res**2)

def initial_and_boundary_loss(model, S_t_ic, S_t_bc_low, S_t_bc_high, K, r):
    # 4.1. Initial Condition Loss (t=T)
    S_ic = S_t_ic[:, 0].unsqueeze(1)
    C_pred_ic = model(S_t_ic)
    C_true_ic = initial_condition(S_ic, K)
    loss_ic = torch.mean((C_pred_ic - C_true_ic)**2)

    # 4.2. Boundary Condition Loss (S=S_min)
    t_bc_low = S_t_bc_low[:, 1].unsqueeze(1)
    C_pred_bc_low = model(S_t_bc_low)
    C_true_bc_low = boundary_condition_low(t_bc_low, K, r)
    loss_bc_low = torch.mean((C_pred_bc_low - C_true_bc_low)**2)

    # 4.3. Boundary Condition Loss (S=S_max)
    S_bc_high = S_t_bc_high[:, 0].unsqueeze(1)
    t_bc_high = S_t_bc_high[:, 1].unsqueeze(1)
    C_pred_bc_high = model(S_t_bc_high)
    C_true_bc_high = boundary_condition_high(S_bc_high, t_bc_high, K, r)
    loss_bc_high = torch.mean((C_pred_bc_high - C_true_bc_high)**2)
    
    return loss_ic, loss_bc_low, loss_bc_high

# --- 5. Data/Collocation Point Generation ---
def generate_training_data(N_COL, N_IC, N_BC, S_min, S_max, t_min, t_max):
    # Collocation Points (S_col, t_col) - PDE Domain
    # Sample S and t uniformly in [S_min, S_max] x [t_min, t_max) (excluding t=T for pure PDE)
    # Note: Using t_max-epsilon to avoid overlapping with IC points for numerical stability
    S_col = S_min + (S_max - S_min) * torch.rand(N_COL, 1)
    t_col = t_min + (t_max - 1e-6 - t_min) * torch.rand(N_COL, 1)
    S_t_col = torch.cat([S_col, t_col], dim=1)
    
    # Initial Condition Points (t=T)
    S_ic = S_min + (S_max - S_min) * torch.rand(N_IC, 1)
    t_ic = torch.full_like(S_ic, t_max)
    S_t_ic = torch.cat([S_ic, t_ic], dim=1)
    
    # Boundary Condition Points (S=S_min and S=S_max)
    t_bc = t_min + (t_max - t_min) * torch.rand(N_BC, 1)
    
    # Boundary at S_min
    S_bc_low = torch.full_like(t_bc, S_min)
    S_t_bc_low = torch.cat([S_bc_low, t_bc], dim=1)
    
    # Boundary at S_max
    S_bc_high = torch.full_like(t_bc, S_max)
    S_t_bc_high = torch.cat([S_bc_high, t_bc], dim=1)
    
    return S_t_col, S_t_ic, S_t_bc_low, S_t_bc_high

# --- 6. Training Loop ---
def train_pinn():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Initialize model and optimizer
    model = PINN().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    # Generate training data and move to device
    S_t_col, S_t_ic, S_t_bc_low, S_t_bc_high = generate_training_data(
        N_COL, N_IC, N_BC, S_min, S_max, t_min, t_max)
    
    S_t_col = S_t_col.to(device)
    S_t_ic = S_t_ic.to(device)
    S_t_bc_low = S_t_bc_low.to(device)
    S_t_bc_high = S_t_bc_high.to(device)
    
    # Training
    print("Starting PINN training...")
    history = {'loss': [], 'pde_loss': [], 'ic_loss': [], 'bc_loss': []}
    
    for epoch in range(N_EPOCHS + 1):
        model.train()
        optimizer.zero_grad()
        
        # 1. Compute PDE Loss
        loss_pde = pde_loss(model, S_t_col, K, r, sigma)
        
        # 2. Compute Initial and Boundary Condition Losses
        loss_ic, loss_bc_low, loss_bc_high = initial_and_boundary_loss(
            model, S_t_ic, S_t_bc_low, S_t_bc_high, K, r)
        loss_bc = loss_bc_low + loss_bc_high
        
        # 3. Total Loss (Weighted sum)
        total_loss = (WEIGHTS['pde'] * loss_pde + 
                      WEIGHTS['ic'] * loss_ic + 
                      WEIGHTS['bc'] * loss_bc)
        
        # Backpropagation
        total_loss.backward()
        optimizer.step()
        
        # Logging and Visualization
        if epoch % 2000 == 0 or epoch == N_EPOCHS:
            history['loss'].append(total_loss.item())
            history['pde_loss'].append(loss_pde.item())
            history['ic_loss'].append(loss_ic.item())
            history['bc_loss'].append(loss_bc.item())
            
            print(f"Epoch {epoch}/{N_EPOCHS} | Total Loss: {total_loss.item():.6f} | "
                  f"PDE Loss: {loss_pde.item():.6f} | IC Loss: {loss_ic.item():.6f} | "
                  f"BC Loss: {loss_bc.item():.6f}")

    print("Training finished.")
    return model, history, device

# --- 7. Evaluation and Plotting ---
def evaluate_and_plot(model, device):
    model.eval()
    
    # Create a grid of (S, t) points for plotting
    S_test = torch.linspace(S_min, S_max, 100).to(device)
    t_test = torch.full_like(S_test, t_max / 2) # Evaluate at half-life (t=0.5)
    
    S_t_test = torch.cat([S_test.unsqueeze(1), t_test.unsqueeze(1)], dim=1)
    
    # PINN Prediction
    with torch.no_grad():
        C_pred = model(S_t_test).cpu().numpy().flatten()
        
    # Analytical Solution (for comparison)
    T_analytic = T - t_test[0] # Time to maturity is T-t
    C_true = black_scholes_call(S_test, K, T_analytic, r, sigma).cpu().numpy().flatten()
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(S_test.cpu().numpy(), C_true, 'r-', label='Black-Scholes Analytical')
    plt.plot(S_test.cpu().numpy(), C_pred, 'b--', label='PINN Prediction')
    plt.title(f'European Call Option Price at $t = {t_test[0].item():.2f}$')
    plt.xlabel('Stock Price (S)')
    plt.ylabel('Option Price (C)')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    # Run the full simulation
    trained_model, loss_history, device = train_pinn()
    evaluate_and_plot(trained_model, device)