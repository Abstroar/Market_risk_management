import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Load the dataset
file_path = "AAPL_stock_data.csv"
df = pd.read_csv(file_path)

# Data Cleaning
# Remove first two rows (metadata) and reset index
df_cleaned = df.iloc[2:].reset_index(drop=True)

# Convert columns to numeric types
numeric_columns = ["Close", "High", "Low", "Open", "Volume"]
df_cleaned[numeric_columns] = df_cleaned[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Convert 'Price' column to datetime format
df_cleaned.rename(columns={"Price": "Date"}, inplace=True)
df_cleaned["Date"] = pd.to_datetime(df_cleaned["Date"], errors='coerce')

# Define features and target variable
X = df_cleaned[["Open", "High", "Low", "Volume"]]  # Features
y = df_cleaned["Close"]  # Target variable (closing price as financial indicator)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Linear Regression Model
model = LinearRegression()
model.fit(X_train, y_train)

# Make Predictions
y_pred = model.predict(X_test)

# Evaluate the Model
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

# Print Performance Metrics
print(f"Mean Absolute Error (MAE): {mae}")
print(f"Mean Squared Error (MSE): {mse}")
print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"R-squared (R2): {r2}")

# Plot Actual vs Predicted Values
plt.figure(figsize=(10, 5))
plt.scatter(y_test, y_pred, alpha=0.5, color='blue')
plt.xlabel("Actual Close Price")
plt.ylabel("Predicted Close Price")
plt.title("Actual vs Predicted Closing Prices")
plt.show()