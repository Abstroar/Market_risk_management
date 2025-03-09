from fastapi import FastAPI
import yfinance as yf
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import uvicorn

# Load Trained Model
model = tf.keras.models.load_model('model.h5')
scaler = MinMaxScaler(feature_range=(0, 1))

app = FastAPI()

@app.get("/predict/{ticker}")
def predict_stock(ticker: str, days: int = 30):
    # Fetch latest data
    stock_data = yf.download(ticker, period='5y', interval='1d')
    close_prices = stock_data['Close'].values.reshape(-1, 1)

    # Scale Data
    scaled_data = scaler.fit_transform(close_prices)
    x_input = scaled_data[-60:]
    x_input = np.reshape(x_input, (1, x_input.shape[0], 1))

    # Predict Future Prices
    predictions = []
    for _ in range(days):
        pred = model.predict(x_input)[0][0]
        predictions.append(pred)
        x_input = np.append(x_input[:,1:,:], [[[pred]]], axis=1)

    # Inverse Scale Predictions
    predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))

    return {
        "stock": ticker,
        "predicted_prices": predictions.flatten().tolist()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)