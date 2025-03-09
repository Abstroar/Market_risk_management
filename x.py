import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import yfinance as yf

# Fetch stock data
ticker = "AAPL"
df = yf.download(ticker, start="2015-01-01", end="2024-01-01")


df['Returns'] = df['Close'].pct_change()

# Calculate rolling volatility (Risk Measure)
df['Volatility'] = df['Returns'].rolling(window=60).std()

# Calculate Value at Risk (VaR) at 95% confidence level
def calculate_var(returns, confidence_level=0.05):
    return np.percentile(returns.dropna(), confidence_level * 100)

df['VaR'] = df['Returns'].rolling(window=60).apply(lambda x: calculate_var(x))

# Calculate Conditional VaR (CVaR)
def calculate_cvar(returns, confidence_level=0.05):
    var = calculate_var(returns, confidence_level)
    return returns[returns <= var].mean()

df['CVaR'] = df['Returns'].rolling(window=60).apply(lambda x: calculate_cvar(x))

# Selecting the 'Close' price for prediction
data = df[['Close']].values

# Normalize data
scaler = MinMaxScaler(feature_range=(0,1))
data_scaled = scaler.fit_transform(data)

# Create sequences
def create_sequences(data, time_step=60):
    X, y = [], []
    for i in range(len(data) - time_step):
        X.append(data[i:i+time_step])
        y.append(data[i+time_step])
    return np.array(X), np.array(y)

time_step = 60
X, y = create_sequences(data_scaled, time_step)

# Split into train and test sets
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Build LSTM Model
model = Sequential([
    LSTM(units=50, return_sequences=True, input_shape=(time_step, 1)),
    Dropout(0.2),
    LSTM(units=50, return_sequences=False),
    Dropout(0.2),
    Dense(units=25),
    Dense(units=1)
])

model.compile(optimizer='adam', loss='mean_squared_error')

# Train model
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

# Predict and inverse transform
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)
y_test_actual = scaler.inverse_transform(y_test.reshape(-1,1))

# Calculate RMSE
rmse = np.sqrt(mean_squared_error(y_test_actual, predictions))
print(f"RMSE: {rmse}")

# Plot results
plt.figure(figsize=(14,6))
plt.plot(df.index[split+time_step:], y_test_actual, label='Actual Prices', color='blue')
plt.plot(df.index[split+time_step:], predictions, label='Predicted Prices', color='red')
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.legend()
plt.show()

# Plot risk measures
plt.figure(figsize=(14,6))
plt.plot(df.index, df['Volatility'], label='Volatility', color='orange')
plt.plot(df.index, df['VaR'], label='VaR (95%)', color='red')
plt.plot(df.index, df['CVaR'], label='CVaR (95%)', color='purple')
plt.xlabel('Date')
plt.ylabel('Risk Measures')
plt.legend()
plt.title('Stock Risk Analysis')
plt.show()
