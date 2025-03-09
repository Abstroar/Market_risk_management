from fastapi import FastAPI
import yfinance as yf
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import uvicorn

app = FastAPI()

# Load LSTM Model
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(64, return_sequences=True, input_shape=(60, 1)),
    tf.keras.layers.LSTM(64, return_sequences=False),
    tf.keras.layers.Dense(25),
    tf.keras.layers.Dense(1)
])
model.compile(optimizer='adam', loss='mean_squared_error')

# Preprocessing Function
scaler = MinMaxScaler(feature_range=(0, 1))


def prepare_data(ticker):
    stock_data = yf.download(ticker, period='5y', interval='1d')
    close_prices = stock_data['Close'].values.reshape(-1, 1)
    scaled_data = scaler.fit_transform(close_prices)

    # Prepare Data for LSTM
    x_test, y_test = [], []
    for i in range(60, len(scaled_data)):
        x_test.append(scaled_data[i - 60:i, 0])
        y_test.append(scaled_data[i, 0])
    x_test, y_test = np.array(x_test), np.array(y_test)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

    return x_test, y_test, scaler.inverse_transform(scaled_data)


@app.get("/predict/{ticker}")
def predict_stock(ticker: str):
    x_test, y_test, full_data = prepare_data(ticker)
    predictions = model.predict(x_test)
    predictions = scaler.inverse_transform(predictions)

    # Return Last 5 Days Prediction
    return {
        "stock": ticker,
        "last_5_days_prediction": predictions[-5:].tolist(),
        "actual_last_5_days": full_data[-5:].tolist()
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
