#!/usr/bin/env python3
"""
Example script demonstrating portfolio access functionality.
This fetches portfolio holdings, positions, and margins from Kite Connect API.
"""
import sys
import os
import pandas as pd

# Import from parent directory (src)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from portfolio_manager import PortfolioManager

def main():
    """Demonstrate portfolio access functionality."""
    print("Portfolio Access Example")
    print("=" * 50)
    
    try:
        # Initialize the portfolio manager
        portfolio_manager = PortfolioManager()
        
        # 1. Fetch Portfolio Holdings
        print("\n1. Portfolio Holdings")
        print("-" * 30)
        holdings_df = portfolio_manager.get_portfolio_holdings()
        
        if not holdings_df.empty:
            print(f"✓ Successfully fetched {len(holdings_df)} holdings")
            print(f"Columns available: {list(holdings_df.columns)}")
            
            # Display key information
            if 'tradingsymbol' in holdings_df.columns and 'quantity' in holdings_df.columns:
                print("\nHoldings Summary:")
                for _, row in holdings_df.iterrows():
                    symbol = row.get('tradingsymbol', 'Unknown')
                    quantity = row.get('quantity', 0)
                    last_price = row.get('last_price', 0)
                    market_value = row.get('market_value', 0)
                    
                    print(f"  {symbol}: {quantity} shares @ ₹{last_price:.2f} = ₹{market_value:,.2f}")
                    
                    # Show P&L if available
                    if 'pnl' in row:
                        pnl = row['pnl']
                        pnl_color = "🟢" if pnl >= 0 else "🔴"
                        print(f"    P&L: {pnl_color} ₹{pnl:,.2f}")
        else:
            print("⚠ No holdings found or error occurred")
        
        # 2. Fetch Positions
        print("\n\n2. Current Positions")
        print("-" * 30)
        positions = portfolio_manager.get_positions()
        
        day_positions = positions.get('day', pd.DataFrame())
        net_positions = positions.get('net', pd.DataFrame())
        
        if not day_positions.empty:
            print(f"✓ Day Positions: {len(day_positions)} positions")
            print("Day Positions:")
            for _, row in day_positions.iterrows():
                symbol = row.get('tradingsymbol', 'Unknown')
                quantity = row.get('quantity', 0)
                print(f"  {symbol}: {quantity} shares")
        else:
            print("⚠ No day positions found")
        
        if not net_positions.empty:
            print(f"✓ Net Positions: {len(net_positions)} positions")
            print("Net Positions:")
            for _, row in net_positions.iterrows():
                symbol = row.get('tradingsymbol', 'Unknown')
                quantity = row.get('quantity', 0)
                print(f"  {symbol}: {quantity} shares")
        else:
            print("⚠ No net positions found")
        
        # 3. Fetch Margins
        print("\n\n3. Margin Information")
        print("-" * 30)
        margins = portfolio_manager.get_margins()
        
        if margins:
            print("✓ Margin information fetched")
            print("Available margin keys:", list(margins.keys()))
            
            # Display equity margin if available
            if 'equity' in margins:
                equity = margins['equity']
                print("\nEquity Margin:")
                for key, value in equity.items():
                    if isinstance(value, (int, float)):
                        print(f"  {key}: ₹{value:,.2f}")
                    else:
                        print(f"  {key}: {value}")
        else:
            print("⚠ No margin information available")
        
        # 4. Comprehensive Portfolio Summary
        print("\n\n4. Portfolio Summary")
        print("-" * 30)
        summary = portfolio_manager.get_portfolio_summary()
        
        if 'portfolio_stats' in summary:
            stats = summary['portfolio_stats']
            print("Portfolio Statistics:")
            print(f"  Total Holdings: {stats.get('num_holdings', 0)}")
            print(f"  Total Value: ₹{stats.get('total_value', 0):,.2f}")
            print(f"  Total Quantity: {stats.get('total_quantity', 0)}")
            
            if 'total_pnl' in stats:
                total_pnl = stats['total_pnl']
                pnl_color = "🟢" if total_pnl >= 0 else "🔴"
                print(f"  Total P&L: {pnl_color} ₹{total_pnl:,.2f}")
        else:
            print("⚠ No portfolio statistics available")
        
        print("\n" + "=" * 50)
        print("Portfolio access example completed!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 