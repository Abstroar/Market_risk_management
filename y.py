import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import yfinance as yf
import pandas_datareader as pdr
from datetime import datetime

# Fetch stock data using Yahoo Finance
ticker = "AAPL"  # Change to any stock symbol
df = yf.download(ticker, start="2015-01-01", end="2024-01-01")

# Reset index to ensure a single-level index
df.reset_index(inplace=True)

# Fetch economic indicators
# Fetch economic indicators
econ_data = pdr.get_data_fred(['DFF', 'CPIAUCSL', 'GDP'], start="2015-01-01", end="2024-01-01")

# Forward-fill missing values in economic data
econ_data.ffill(inplace=True)

# Reset index to ensure a single-level index
econ_data.reset_index(inplace=True)

# Rename the date column to match `df`
econ_data.rename(columns={'DATE': 'Date'}, inplace=True)

# Ensure `Date` column in both DataFrames is of the same type
df['Date'] = pd.to_datetime(df['Date'])
econ_data['Date'] = pd.to_datetime(econ_data['Date'])

# Flatten multi-index if present (important fix)
if isinstance(econ_data.columns, pd.MultiIndex):
    econ_data.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in econ_data.columns]

# Merge stock data with economic data
df = df.merge(econ_data, how='left', on='Date')

# Set index back to Date
df.set_index('Date', inplace=True)


# Calculate daily returns
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

# Selecting relevant features for prediction
features = ['Close', 'DFF', 'CPIAUCSL', 'GDP', 'Volatility', 'VaR', 'CVaR']
data = df[features].dropna().values

# Normalize data
scaler = MinMaxScaler(feature_range=(0,1))
data_scaled = scaler.fit_transform(data)

# Create sequences
def create_sequences(data, time_step=60):
    X, y = [], []
    for i in range(len(data) - time_step):
        X.append(data[i:i+time_step])
        y.append(data[i+time_step, -1])  # Predicting risk
    return np.array(X), np.array(y)

time_step = 60
X, y = create_sequences(data_scaled, time_step)

# Split into train and test sets
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Build LSTM Model
model = Sequential([
    LSTM(units=50, return_sequences=True, input_shape=(time_step, X.shape[2])),
    Dropout(0.2),
    LSTM(units=50, return_sequences=False),
    Dropout(0.2),
    Dense(units=25),
    Dense(units=1, activation='sigmoid')  # Output risk as percentage (0-100%)
])

model.compile(optimizer='adam', loss='mean_squared_error')

# Train model
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

# Predict and inverse transform
predictions = model.predict(X_test) * 100  # Convert to percentage (0-100%)
y_test_actual = y_test * 100

# Calculate RMSE
rmse = np.sqrt(mean_squared_error(y_test_actual, predictions))
print(f"RMSE: {rmse}")

# Plot results
plt.figure(figsize=(14,6))
plt.plot(df.index[split+time_step:], y_test_actual, label='Actual Risk (%)', color='blue')
plt.plot(df.index[split+time_step:], predictions, label='Predicted Risk (%)', color='red')
plt.xlabel('Date')
plt.ylabel('Risk Percentage')
plt.legend()
plt.title('Stock Risk Prediction')
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
