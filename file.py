# --- Market Risk Analysis Pipeline with Alpha Vantage, LSTM-RF, and Plot Returns ---

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from alpha_vantage.timeseries import TimeSeries
import joblib
import os

# --- Function 1: Fetch & Preprocess Stock Data ---
def fetch_and_preprocess_data(api_key, symbols, interval='15min'):
    ts = TimeSeries(key=api_key, output_format='pandas', indexing_type='date')
    stock_data = {}
    log = []

    for symbol in symbols:
        try:
            data, _ = ts.get_intraday(symbol=symbol, interval=interval, outputsize='full')
            data = data.rename(columns={'4. close': 'current_price'})
            data['Returns'] = data['current_price'].pct_change()
            data['Intraday_Volatility'] = data['Returns'].rolling(window=10).std()
            data['Volume_Ratio'] = data['5. volume'] / data['5. volume'].rolling(window=10).mean()

            stock_data[symbol] = {
                'prices': data['current_price'],
                'returns': data['Returns'],
                'volatility': data['Intraday_Volatility'],
                'volume': data['5. volume'],
                'volume_ratio': data['Volume_Ratio'],
                'raw_data': data
            }
            log.append(f"Fetched and processed: {symbol}")
        except Exception as e:
            log.append(f"Error with {symbol}: {e}")

    return stock_data, log

# --- Function 2: Train LSTM + Random Forest Hybrid Model ---
def train_hybrid_model(stock_data, model_save_path):
    X, y = [], []
    for stock in stock_data.values():
        prices = stock['prices'].dropna().values
        for i in range(50, len(prices)):
            X.append(prices[i-50:i])
            y.append(prices[i])

    X, y = np.array(X), np.array(y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train_lstm = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_test_lstm = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    # LSTM
    lstm_model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(X_train_lstm.shape[1], 1)),
        LSTM(units=50),
        Dense(1)
    ])
    lstm_model.compile(optimizer='adam', loss='mean_squared_error')
    lstm_model.fit(X_train_lstm, y_train, epochs=50, batch_size=32, verbose=0)

    # Random Forest
    rf_model = RandomForestRegressor(n_estimators=100)
    rf_model.fit(X_train, y_train)

    # Evaluation
    y_pred_lstm = lstm_model.predict(X_test_lstm)
    mse = mean_squared_error(y_test, y_pred_lstm)
    r2 = r2_score(y_test, y_pred_lstm)

    # Save
    lstm_path = os.path.join(model_save_path, 'lstm_model.h5')
    rf_path = os.path.join(model_save_path, 'rf_model.pkl')
    lstm_model.save(lstm_path)
    joblib.dump(rf_model, rf_path)

    return {
        "mse": mse,
        "r2_score": r2,
        "lstm_model_path": lstm_path,
        "rf_model_path": rf_path
    }

# --- Function 3: Plot Risk Factors and Return Figures ---
def plot_risk_factors(stock_data):
    figures = {}
    for symbol, metrics in stock_data.items():
        fig, axs = plt.subplots(3, 2, figsize=(18, 12))
        fig.suptitle(f"Intraday Risk Analysis for {symbol}", fontsize=20)

        axs[0, 0].plot(metrics['prices'], color='blue')
        axs[0, 0].set_title('1. Closing Price')
        axs[0, 1].plot(metrics['returns'], color='green')
        axs[0, 1].set_title('2. Returns')
        axs[1, 0].plot(metrics['volatility'], color='red')
        axs[1, 0].set_title('3. Volatility')
        axs[1, 1].plot(metrics['volume'], color='orange')
        axs[1, 1].set_title('4. Volume')
        axs[2, 0].plot(metrics['volume_ratio'], color='purple')
        axs[2, 0].set_title('5. Volume Ratio')
        axs[2, 1].axis('off')

        for ax in axs.flat:
            ax.grid(True)
            ax.label_outer()

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        figures[symbol] = fig
        plt.close(fig)

    return figures

# --- Function 4: Full Pipeline Wrapper ---
def market_risk_pipeline(api_key, save_dir):
    symbols = ['AAPL', 'MSFT', 'GOOG', 'AMZN']
    stock_data, fetch_log = fetch_and_preprocess_data(api_key, symbols)
    model_results = train_hybrid_model(stock_data, save_dir)
    risk_figures = plot_risk_factors(stock_data)

    return {
        "logs": fetch_log,
        "model_results": model_results,
        "risk_plots": risk_figures
    }

# --- Execution Entry Point ---
if __name__ == "__main__":
    results = market_risk_pipeline(
        api_key='YOUR_ALPHA_VANTAGE_API_KEY',
        save_dir='C:/Users/dolit/OneDrive/Desktop/College/Capstone Project/Market Risk Assesment'
    )

    print("\n✅ MODEL RESULTS")
    print(results["model_results"])

    print("\n✅ STOCKS PROCESSED")
    print(list(results["risk_plots"].keys()))