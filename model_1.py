import yfinance as yf

# Fetch stock data for Reliance Industries
stock = yf.Ticker("RELIANCE.NS")
data = stock.history(period="1mo")  # Last 1 month data
print(data)
