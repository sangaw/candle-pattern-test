import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from torch.autograd import grad
from scipy.stats import norm

# --- 1. Black-Scholes Parameters and Domain ---
# (Parameters must match the training script)
K = 100.0   # Strike Price
r = 0.05    # Risk-free rate
sigma = 0.2 # Volatility
T = 1.0     # Time to maturity (years)

# Computational Domain for (S, t)
S_min = 50.0
S_max = 150.0
t_min = 0.0
t_max = T

# Training Hyperparameters (Set to the values used in the previous run)
N_COL = 10000
N_IC = 1000
N_BC = 1000
N_EPOCHS = 20000
LEARNING_RATE = 1e-3
WEIGHTS = {'pde': 1.0, 'ic': 100.0, 'bc': 100.0}

# --- 2. Supporting Functions (from previous code) ---

def black_scholes_call(S, K, T, r, sigma):
    # T here is 'time to maturity' (T - t in the PDE context)
    d1 = (torch.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * torch.sqrt(T))
    d2 = d1 - sigma * torch.sqrt(T)
    
    # Detach and convert to NumPy for scipy's norm.cdf, then convert back to tensor
    d1_np = d1.detach().cpu().numpy()
    d2_np = d2.detach().cpu().numpy()
    
    # Ensure T is not zero, which would cause an error in d1/d2 calculation
    if T.item() == 0:
        call_price_np = np.maximum(S.detach().cpu().numpy() - K, 0)
    else:
        call_price_np = S.detach().cpu().numpy() * norm.cdf(d1_np) - K * torch.exp(-r * T).item() * norm.cdf(d2_np)
        
    return torch.tensor(call_price_np, dtype=torch.float32).to(S.device)

def initial_condition(S, K):
    return torch.relu(S - K)

def boundary_condition_low(t, K, r):
    return torch.zeros_like(t) 

def boundary_condition_high(S, t, K, r):
    time_to_maturity = T - t
    return S - K * torch.exp(-r * time_to_maturity)

# --- 3. PINN Model Definition (from previous code) ---
class PINN(nn.Module):
    def __init__(self):
        super(PINN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(2, 50), nn.Tanh(),
            nn.Linear(50, 50), nn.Tanh(),
            nn.Linear(50, 50), nn.Tanh(),
            nn.Linear(50, 1)
        )
        nn.init.xavier_uniform_(self.net[0].weight)

    def forward(self, x):
        return self.net(x)

def pde_loss(model, S_t_col, K, r, sigma):
    S = S_t_col[:, 0].unsqueeze(1).requires_grad_(True)
    t = S_t_col[:, 1].unsqueeze(1).requires_grad_(True)
    C = model(torch.cat([S, t], dim=1))
    
    dC_dS = grad(C, S, grad_outputs=torch.ones_like(C), create_graph=True)[0]
    dC_dt = grad(C, t, grad_outputs=torch.ones_like(C), create_graph=True)[0]
    d2C_dS2 = grad(dC_dS, S, grad_outputs=torch.ones_like(dC_dS), create_graph=True)[0]
    
    # Black-Scholes PDE Residual
    pde_res = dC_dt + 0.5 * sigma**2 * S**2 * d2C_dS2 + r * S * dC_dS - r * C
    return torch.mean(pde_res**2)

def initial_and_boundary_loss(model, S_t_ic, S_t_bc_low, S_t_bc_high, K, r):
    # IC Loss
    S_ic = S_t_ic[:, 0].unsqueeze(1)
    C_pred_ic = model(S_t_ic)
    C_true_ic = initial_condition(S_ic, K)
    loss_ic = torch.mean((C_pred_ic - C_true_ic)**2)

    # BC Low Loss
    t_bc_low = S_t_bc_low[:, 1].unsqueeze(1)
    C_pred_bc_low = model(S_t_bc_low)
    C_true_bc_low = boundary_condition_low(t_bc_low, K, r)
    loss_bc_low = torch.mean((C_pred_bc_low - C_true_bc_low)**2)

    # BC High Loss
    S_bc_high = S_t_bc_high[:, 0].unsqueeze(1)
    t_bc_high = S_t_bc_high[:, 1].unsqueeze(1)
    C_pred_bc_high = model(S_t_bc_high)
    C_true_bc_high = boundary_condition_high(S_bc_high, t_bc_high, K, r)
    loss_bc_high = torch.mean((C_pred_bc_high - C_true_bc_high)**2)
    
    return loss_ic, loss_bc_low, loss_bc_high

def generate_training_data(N_COL, N_IC, N_BC, S_min, S_max, t_min, t_max):
    S_col = S_min + (S_max - S_min) * torch.rand(N_COL, 1)
    t_col = t_min + (t_max - 1e-6 - t_min) * torch.rand(N_COL, 1)
    S_t_col = torch.cat([S_col, t_col], dim=1)
    
    S_ic = S_min + (S_max - S_min) * torch.rand(N_IC, 1)
    t_ic = torch.full_like(S_ic, t_max)
    S_t_ic = torch.cat([S_ic, t_ic], dim=1)
    
    t_bc = t_min + (t_max - t_min) * torch.rand(N_BC, 1)
    S_bc_low = torch.full_like(t_bc, S_min)
    S_t_bc_low = torch.cat([S_bc_low, t_bc], dim=1)
    
    S_bc_high = torch.full_like(t_bc, S_max)
    S_t_bc_high = torch.cat([S_bc_high, t_bc], dim=1)
    
    return S_t_col, S_t_ic, S_t_bc_low, S_t_bc_high

def train_pinn():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    model = PINN().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    S_t_col, S_t_ic, S_t_bc_low, S_t_bc_high = generate_training_data(
        N_COL, N_IC, N_BC, S_min, S_max, t_min, t_max)
    
    S_t_col = S_t_col.to(device)
    S_t_ic = S_t_ic.to(device)
    S_t_bc_low = S_t_bc_low.to(device)
    S_t_bc_high = S_t_bc_high.to(device)
    
    print("Starting PINN training...")
    
    for epoch in range(N_EPOCHS + 1):
        model.train()
        optimizer.zero_grad()
        
        loss_pde = pde_loss(model, S_t_col, K, r, sigma)
        
        loss_ic, loss_bc_low, loss_bc_high = initial_and_boundary_loss(
            model, S_t_ic, S_t_bc_low, S_t_bc_high, K, r)
        loss_bc = loss_bc_low + loss_bc_high
        
        total_loss = (WEIGHTS['pde'] * loss_pde + 
                      WEIGHTS['ic'] * loss_ic + 
                      WEIGHTS['bc'] * loss_bc)
        
        total_loss.backward()
        optimizer.step()
        
        if epoch % 5000 == 0 or epoch == N_EPOCHS:
            print(f"Epoch {epoch}/{N_EPOCHS} | Total Loss: {total_loss.item():.6f} | "
                  f"PDE Loss: {loss_pde.item():.6f} | IC Loss: {loss_ic.item():.6f} | "
                  f"BC Loss: {loss_bc.item():.6f}")

    print("Training finished.")
    return model, device

# --- 4. Evaluation and Plotting Function ---
def evaluate_and_plot(model, device):
    model.eval()
    
    # Create a dense grid of Stock Prices (S) for plotting
    S_test = torch.linspace(S_min, S_max, 200).to(device)
    
    # *** Time Slice for Visualization (T/2 = 0.5 years) ***
    t_plot = 0.5 
    t_test = torch.full_like(S_test, t_plot)
    
    S_t_test = torch.cat([S_test.unsqueeze(1), t_test.unsqueeze(1)], dim=1)
    
    # PINN Prediction
    with torch.no_grad():
        C_pred = model(S_t_test).cpu().numpy().flatten()
        
    # Analytical Solution (T_analytic is the remaining time to maturity)
    T_analytic = T - t_plot 
    T_analytic_tensor = torch.full_like(S_test, T_analytic)
    C_true = black_scholes_call(S_test, K, T_analytic_tensor, r, sigma).cpu().numpy().flatten()
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(S_test.cpu().numpy(), C_true, 'r-', linewidth=3, label='Black-Scholes Analytical (True)')
    plt.plot(S_test.cpu().numpy(), C_pred, 'b--', linewidth=2, label='PINN Prediction')
    plt.title(f'European Call Option Price ($K={K}, T={T}$): $t = {t_plot}$', fontsize=14)
    plt.xlabel('Stock Price (S)', fontsize=12)
    plt.ylabel('Option Price (C)', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()

# --- 5. Main Execution ---
if __name__ == '__main__':
    # Run the full simulation
    trained_model, device = train_pinn()
    evaluate_and_plot(trained_model, device)