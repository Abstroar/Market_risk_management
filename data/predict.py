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

# Compute Daily Returns
df_cleaned['Returns'] = df_cleaned['Close'].pct_change()

# Calculate Value at Risk (VaR)
confidence_level = 0.05  # 95% confidence
var_95 = df_cleaned['Returns'].quantile(confidence_level)

# Calculate Conditional VaR (CVaR)
cvar_95 = df_cleaned['Returns'][df_cleaned['Returns'] <= var_95].mean()

# Print Risk Metrics
print(f"95% Value at Risk (VaR): {var_95:.4f}")
print(f"95% Conditional VaR (CVaR): {cvar_95:.4f}")

# Plot Returns Distribution
plt.figure(figsize=(10, 5))
plt.hist(df_cleaned['Returns'].dropna(), bins=50, color='blue', alpha=0.7)
plt.axvline(var_95, color='red', linestyle='dashed', label=f'95% VaR: {var_95:.4f}')
plt.axvline(cvar_95, color='orange', linestyle='dashed', label=f'95% CVaR: {cvar_95:.4f}')
plt.xlabel("Daily Returns")
plt.ylabel("Frequency")
plt.title("Distribution of Daily Returns with VaR and CVaR")
plt.legend()
plt.show()
