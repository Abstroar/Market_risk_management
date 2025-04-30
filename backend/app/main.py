from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime, timedelta
import requests
import os
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from get_stock_data import StockDataResponse, StockDataService
from home_data import *
# from load_model import load_model
# from labeling import label_risk
# from data_collection import get_stock_data
# from data_preprocessing import preprocess_data
# from feature_engineering import add_features

app = FastAPI()

# CORS setup (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
db = client.stock_db
collection = db.stock_prices

# Reuse Finnhub API logic from fetcherdaily.py
FINNHUB_API_KEY = "d02p359r01qi6jgif6p0d02p359r01qi6jgif6pg"  # Move to .env later
FINNHUB_URL = "https://finnhub.io/api/v1/quote"

class StockData(BaseModel):
    symbol: str
    value: float
    timestamp: datetime


class StockDataResponse(BaseModel):
    date: str
    avg_close: float

@app.get("/stocks/{symbol}", response_model=list[StockDataResponse])
def get_stock_data(
    symbol: str,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD"),
    aggregate: Optional[str] = Query("monthly", description="Aggregate by 'monthly' or 'yearly'")):
    print(f"Start Date: {start_date}, End Date: {end_date}, Aggregate: {aggregate}")
    stock_service = StockDataService(collection_name=symbol.lower())
    try:
        data = stock_service.get_stock_data_from_db(start_date, end_date, aggregate)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/stocks")
def get_all_stocks():
    raw_data = get_all_stocks_data()
    cleaned = [clean_stock_data(stock) for stock in raw_data]
    return cleaned

# def fetch_stock_price(symbol: str):
#     """Fetch stock price from Finnhub (same as fetcherdaily.py)"""
#     try:
#         response = requests.get(
#             FINNHUB_URL,
#             params={"symbol": symbol, "token": FINNHUB_API_KEY}
#         )
#         response.raise_for_status()
#         data = response.json()
#         if "c" not in data:
#             raise HTTPException(status_code=404, detail="Stock not found in API")
#         return {
#             "symbol": symbol,
#             "value": data["c"],
#             "timestamp": datetime.utcnow()
#         }
#     except requests.exceptions.RequestException as e:
#         raise HTTPException(status_code=500, detail=f"API error: {e}")
#
#
# @app.route('/api/analyze/<ticker>')
# def analyze_api(ticker):
#     try:
#         # Get stock data and analyze
#         data = get_stock_data(ticker.upper())
#         data = preprocess_data(data)
#         data = add_features(data)
#         data = label_risk(data)
#
#         # Load the model
#         model = load_model()
#
#         # Get features for prediction
#         features = ['Daily Return', 'Volatility', 'MA50', 'MA200']
#         latest_data = data[features].iloc[-1]
#
#         # Make prediction
#         risk_level = model.predict(latest_data.values.reshape(1, -1))[0]
#
#         # Prepare API response
#         response = {
#             'ticker': ticker.upper(),
#             'analysis': {
#                 'risk_level': int(risk_level),
#                 'current_price': float(data['Close'].iloc[-1]),
#                 'volatility': float(data['Volatility'].iloc[-1]),
#                 'daily_return': float(data['Daily Return'].iloc[-1]),
#                 'last_updated': data.index[-1].isoformat()
#             },
#             'historical_data': {
#                 'dates': [d.isoformat() for d in data.index[-30:]],
#                 'prices': [float(p) for p in data['Close'].tail(30)]
#             }
#         }
#
#         return response
#     except Exception as e:
#         import traceback
#         import logging
#         logging.error(traceback.format_exc())  # Log the full error on the server
#         return {
#             'error': 'An internal error has occurred.',
#             'ticker': ticker.upper()
#         }, 400
#
# @app.get("/get-stock/{symbol}")
# async def get_stock(symbol: str):
#     # 1. Check MongoDB for existing data
#     stock = collection.find_one(
#         {"symbol": symbol},
#         sort=[("timestamp", -1)]  # Get most recent record
#     )
#
#     # 2. If no data or data is older than 24 hours, fetch fresh data
#     if not stock or (datetime.utcnow() - stock["timestamp"] > timedelta(hours=24)):
#         try:
#             fresh_data = fetch_stock_price(symbol)
#             collection.insert_one(fresh_data)  # Save to DB
#             return fresh_data
#         except HTTPException as e:
#             raise e
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=str(e))
#
#     # 3. Return cached data if fresh
#     return {
#         "symbol": stock["symbol"],
#         "value": stock["value"],
#         "timestamp": stock["timestamp"]
#     }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)