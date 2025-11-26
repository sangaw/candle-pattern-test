# Initialization Prompts

Please familirize yourself with the code and comments. We will do further enhancements today.

How to generate access token using the python code. Please provide the command to run

myenv\Scripts\activate

python src/auth/get_request_token.py
# (Follow browser steps, copy request token)

python src/auth/token_generator.py
# (Follow prompts to generate and save access token)

Set-ExecutionPolicy -Scope Process RemoteSigned

   cd candle-pattern-test
   python -m venv myenv
   myenv\Scripts\activate
   ```

2. **Install the required dependencies**:
   ```bash
   pip install -r ..\requirements.txt
   ```

   Or install kiteconnect specifically:
   ```bash
   pip install kiteconnect>=4.2.0
   ```

3. **Alternative: Install all dependencies at once**:
   ```bash
   pip install requests pandas numpy kiteconnect matplotlib seaborn pytest pytest-cov pytest-mock black flake8 mypy python-dateutil python-dotenv pydantic pydantic-ai ta scikit-learn
   ```


   Run example_feature_engineering.py to merge all CSV files
   Run Dow Theory example_daily_dowtheory to add trend indicators
   Final CSV with all features will be full_featured.csv



✅ Final Backtest Results:
----------------------------------------
Instrument: Nifty 50 Index
Test Period Length: 120 days
Total Trades Executed: 1
Total Return: 183.55%
Final Net Worth: $28,355,000.00
Max Drawdown Constraint: 10.00%
Actual Max Drawdown Observed: 17.06%
----------------------------------------