from flask import Flask, jsonify, request
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

app = Flask(__name__)
CORS(app)

# Load the regression model
MODEL_PATH = r'C:\Users\Sandeep\Documents\Work\code\candle-pattern-test\model\dow_theory_trend_regression_model.pkl'

model = None

def load_model():
    global model
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        print(f"✓ Model loaded successfully from {MODEL_PATH}")
        return True
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return False

def fetch_nifty_data(days=90):
    """Fetch Nifty 50 historical data"""
    try:
        # Nifty 50 symbol for yfinance
        nifty = yf.Ticker("^NSEI")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        df = nifty.history(start=start_date, end=end_date)
        df.reset_index(inplace=True)
        
        # Rename columns to match expected format
        df = df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Format date
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        return df[['date', 'open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def analyze_dow_theory(df):
    """Analyze Dow Theory trend based on price action"""
    if len(df) < 10:
        return 'neutral'
    
    recent = df.tail(10)
    highs = recent['high'].values
    lows = recent['low'].values
    
    # Check for higher highs and higher lows
    higher_highs = highs[-1] > highs[-3] and highs[-3] > highs[-5]
    higher_lows = lows[-1] > lows[-3] and lows[-3] > lows[-5]
    
    # Check for lower highs and lower lows
    lower_highs = highs[-1] < highs[-3] and highs[-3] < highs[-5]
    lower_lows = lows[-1] < lows[-3] and lows[-3] < lows[-5]
    
    if higher_highs and higher_lows:
        return 'bullish'
    elif lower_highs and lower_lows:
        return 'bearish'
    else:
        return 'neutral'

def prepare_model_input(df):
    """Prepare data for model prediction"""
    # Create a copy for model input
    model_df = df.copy()
    
    # Add technical indicators if needed by your model
    # Example: Moving averages, RSI, etc.
    model_df['ma_5'] = model_df['close'].rolling(window=5).mean()
    model_df['ma_20'] = model_df['close'].rolling(window=20).mean()
    model_df['volatility'] = model_df['close'].rolling(window=10).std()
    
    # Drop NaN values
    model_df = model_df.dropna()
    
    return model_df

def make_prediction(df):
    """Make prediction using the loaded model"""
    if model is None:
        return None
    
    try:
        # Prepare input features
        model_df = prepare_model_input(df)
        
        if len(model_df) == 0:
            return None
        
        # Get the latest row for prediction
        latest = model_df.tail(1)
        
        # Extract features (adjust based on your model's requirements)
        features = latest[['open', 'high', 'low', 'close']].values
        
        # Make prediction
        prediction = model.predict(features)[0]
        
        # Calculate confidence and levels
        current_price = float(latest['close'].values[0])
        
        # Determine trend based on prediction
        trend = 'bullish' if prediction > current_price else 'bearish'
        confidence = min(abs(prediction - current_price) / current_price, 1.0)
        
        return {
            'trend': trend,
            'confidence': float(confidence),
            'predicted_price': float(prediction),
            'current_price': current_price,
            'target_level': float(prediction * 1.02),  # 2% above prediction
            'support_level': float(prediction * 0.98)  # 2% below prediction
        }
    except Exception as e:
        print(f"Prediction error: {e}")
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None
    })

@app.route('/api/nifty-data', methods=['GET'])
def get_nifty_data():
    """Get Nifty 50 historical data"""
    days = request.args.get('days', 90, type=int)
    
    df = fetch_nifty_data(days)
    
    if df is None:
        return jsonify({'error': 'Failed to fetch data'}), 500
    
    # Analyze Dow Theory trend
    dow_trend = analyze_dow_theory(df)
    
    # Get latest price info
    latest = df.tail(1).to_dict('records')[0]
    
    return jsonify({
        'data': df.to_dict('records'),
        'dow_trend': dow_trend,
        'latest_price': latest,
        'data_points': len(df)
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make prediction using the model"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    # Fetch recent data
    df = fetch_nifty_data(days=90)
    
    if df is None:
        return jsonify({'error': 'Failed to fetch data'}), 500
    
    # Make prediction
    prediction = make_prediction(df)
    
    if prediction is None:
        return jsonify({'error': 'Prediction failed'}), 500
    
    return jsonify(prediction)

@app.route('/api/reload-model', methods=['POST'])
def reload_model():
    """Reload the model from disk"""
    success = load_model()
    return jsonify({
        'success': success,
        'model_loaded': model is not None
    })

if __name__ == '__main__':
    print("=" * 50)
    print("Nifty 50 Dow Theory Prediction Server")
    print("=" * 50)
    
    # Load model on startup
    load_model()
    
    print("\nStarting Flask server on http://localhost:5000")
    print("API Endpoints:")
    print("  GET  /api/health       - Health check")
    print("  GET  /api/nifty-data   - Get Nifty data")
    print("  POST /api/predict      - Get ML prediction")
    print("  POST /api/reload-model - Reload model file")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)