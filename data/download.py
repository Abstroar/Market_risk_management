import yfinance as yf

# Download historical stock data
data = yf.download("AAPL", start="2015-01-01", end="2024-01-01")

# Display the first few rows
print(data.head())

# Save to CSV file
data.to_csv("AAPL_stock_data.csv")
