# --- market_risk_predictor.py ---

import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from alpha_vantage.timeseries import TimeSeries
import joblib
import os

# --- CONFIG ---
api_key = 'YOUR_ALPHA_VANTAGE_API_KEY'  # Replace with your actual key
model_path = 'C:/Users/dolit/OneDrive/Desktop/College/Capstone Project/Market Risk Assesment/models'
symbols = ['AAPL', 'MSFT', 'GOOG', 'AMZN']

# --- Fetch Latest Stock Data ---
def fetch_stock_data(symbol):
    ts = TimeSeries(key=api_key, output_format='pandas', indexing_type='date')
    data, _ = ts.get_intraday(symbol=symbol, interval='15min', outputsize='full')
    data = data.rename(columns={'4. close': 'current_price'})
    data['Returns'] = data['current_price'].pct_change()
    data['Volatility'] = data['Returns'].rolling(window=10).std()
    data['Volume_Ratio'] = data['5. volume'] / data['5. volume'].rolling(window=10).mean()
    return data.dropna()

# --- Prepares data for model input ---
def prepare_lstm_input(prices, window_size=50):
    X = []
    for i in range(window_size, len(prices)):
        X.append(prices[i - window_size:i])
    X = np.array(X)
    return X.reshape((X.shape[0], X.shape[1], 1))

def prepare_rf_input(data, window_size=50):
    X = []
    for i in range(window_size, len(data)):
        X.append(data[i - window_size:i])
    return np.array(X)

# --- Predict with LSTM & RF ---
def predict_stock_risk(symbol):
    try:
        # Fetch and prepare data
        data = fetch_stock_data(symbol)
        prices = data['current_price'].values
        X_lstm = prepare_lstm_input(prices)
        X_rf = prepare_rf_input(prices)

        # Load models
        lstm_model = load_model(os.path.join(model_path, 'lstm_model.h5'))
        rf_model = joblib.load(os.path.join(model_path, 'rf_model.pkl'))

        # Predict
        lstm_preds = lstm_model.predict(X_lstm)
        rf_preds = rf_model.predict(X_rf)

        # Get last prediction
        lstm_pred = float(lstm_preds[-1][0])
        rf_pred = float(rf_preds[-1])

        # Risk Metrics
        latest = data.iloc[-1]
        return {
            'symbol': symbol,
            'lstm_prediction': round(lstm_pred, 2),
            'rf_prediction': round(rf_pred, 2),
            'latest_price': round(latest['current_price'], 2),
            'return': round(latest['Returns'] * 100, 2),
            'volatility': round(latest['Volatility'], 6),
            'volume_ratio': round(latest['Volume_Ratio'], 4)
        }

    except Exception as e:
        return {"symbol": symbol, "error": str(e)}

# --- Main Execution ---
if __name__ == '__main__':
    results = []
    for symbol in symbols:
        print(f"\n🔍 Running risk prediction for {symbol}")
        result = predict_stock_risk(symbol)
        results.append(result)
        print(result)
