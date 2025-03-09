import yfinance as yf
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

# Fetch 5 years of combined stock data (AAPL + GOOGL + MSFT)
stocks = ['AAPL', 'GOOGL', 'MSFT','TSLA', 'NVDA', 'AMZN', 'META', 'NFLX', 'AMD', 'IBM']
all_data = []

for ticker in stocks:
    data = yf.download(ticker, period='5y', interval='1d')
    all_data.append(data['Close'].values)

# Combine all data into one array
combined_data = np.concatenate(all_data)

# Preprocess Data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(combined_data.reshape(-1, 1))

# Prepare Training Data
x_train, y_train = [], []
for i in range(60, len(scaled_data)):
    x_train.append(scaled_data[i-60:i, 0])
    y_train.append(scaled_data[i, 0])
x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

# Build and Train Model
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(64, return_sequences=True, input_shape=(60, 1)),
    tf.keras.layers.LSTM(64, return_sequences=False),
    tf.keras.layers.Dense(25),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(x_train, y_train, epochs=20, batch_size=32)

# Save Model
model.save('model.h5')
print("Model trained and saved as model.h5")