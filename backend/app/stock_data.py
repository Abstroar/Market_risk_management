import yfinance as yf
from fastapi import HTTPException
import requests
from datetime import datetime
# def get_stock_data(symbol: str):
#     try:
#         # Fetch the stock data using yfinance
#         stock = yf.Ticker(symbol)
#         data = stock.history(period="1d")  # Get daily data (1 day period)

#         if data.empty:
#             raise HTTPException(status_code=404, detail="Stock not found")

#         # Extract relevant information
#         stock_data = {
#             "symbol": symbol,
#             "current_price": data["Close"].iloc[-1],  # Latest closing price
#             "open_price": data["Open"].iloc[-1],      # Opening price
#             "high_price": data["High"].iloc[-1],      # Highest price of the day
#             "low_price": data["Low"].iloc[-1],        # Lowest price of the day
#             "volume": data["Volume"].iloc[-1],        # Trading volume
#             "date": data.index[-1].strftime("%Y-%m-%d %H:%M:%S")  # Date of the last data point
#         }

#         return stock_data

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching stock data: {e}")
API_KEY = '7bf9b1f7bee44c049e1b4442e7bf278d'
def get_stock_data(symbol: str):
    print("RUNNING")
    url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch data from TwelveData")

    data = response.json()
    if "code" in data:  # TwelveData returns 'code' field if error
        raise HTTPException(status_code=404, detail="Stock not found")

    return {
        "symbol": data["symbol"],
        "current_price": data["close"],
        "open_price": data["open"],
        "high_price": data["high"],
        "low_price": data["low"],
        "volume": data.get("volume"),
        "date": datetime.now()
    }

# stock_data = get_stock_data('AAPL')
# print(stock_data)