from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime, timedelta
import requests
import os
import time
import logging
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from .get_stock_data import StockDataResponse, StockDataService
from .home_data import *
# from load_model import load_model
# from labeling import label_risk
# from data_collection import get_stock_data
# from data_preprocessing import preprocess_data
# from feature_engineering import add_features

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS setup (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup with retry logic
def connect_to_mongodb(max_retries=3, retry_delay=2):
    for attempt in range(max_retries):
        try:
            client = MongoClient(
                "mongodb+srv://abhilaksh:DVH1RDrl4DBUTCaA@capstone.vwbejki.mongodb.net/?retryWrites=true&w=majority&appName=Capstone",
                ssl=True,
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            # Test the connection
            client.admin.command('ping')
            print(f"Successfully connected to MongoDB on attempt {attempt + 1}!")
            return client
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Could not connect to MongoDB.")
                raise

try:
    client = connect_to_mongodb()
    db = client["stock_database"]
    collection = db["stock_data"]
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    raise

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
    try:
        # Validate aggregate parameter
        if aggregate not in ['daily', 'weekly', 'monthly', 'yearly']:
            raise HTTPException(
                status_code=400,
                detail="Invalid aggregate parameter. Must be one of: daily, weekly, monthly, yearly"
            )
            
        # Validate symbol format
        if not symbol.isalpha():
            raise HTTPException(
                status_code=400,
                detail="Invalid symbol format. Must contain only letters"
            )
            
        logger.info(f"Received request for {symbol} from {start_date} to {end_date} with aggregation {aggregate}")
        service = StockDataService()
        data = service.get_stock_data_from_db(start_date, end_date, symbol, aggregate)
        logger.info(f"Returning {len(data)} data points")
        return data
    except ValueError as e:
        logger.error(f"ValueError in get_stock_data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_stock_data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching stock data")

@app.get("/api/stocks")
def get_all_stocks():
    try:
        raw_data = get_all_stocks_data()
        cleaned = [clean_stock_data(stock) for stock in raw_data]
        return cleaned
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock-data")
async def get_stock_data(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    symbol: str = Query(..., description="Stock symbol (e.g., AMZN)"),
    aggregate: str = Query("monthly", description="Aggregation type: daily, weekly, monthly, yearly")
):
    try:
        # Validate aggregate parameter
        if aggregate not in ['daily', 'weekly', 'monthly', 'yearly']:
            raise HTTPException(
                status_code=400,
                detail="Invalid aggregate parameter. Must be one of: daily, weekly, monthly, yearly"
            )
            
        # Validate symbol format
        if not symbol.isalpha():
            raise HTTPException(
                status_code=400,
                detail="Invalid symbol format. Must contain only letters"
            )
            
        service = StockDataService()
        data = service.get_stock_data_from_db(start_date, end_date, symbol, aggregate)
        return {"data": data}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching stock data")

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