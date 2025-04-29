# backend/app/stock_service.py
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
from typing import List, Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class StockDataResponse(BaseModel):
    date: str
    avg_close: float
class StockDataService:
    def __init__(self, db_uri: str = "mongodb+srv://abhilaksh:DVH1RDrl4DBUTCaA@capstone.vwbejki.mongodb.net/?retryWrites=true&w=majority&appName=Capstone", db_name: str = 'stock_database', collection_name: str = 'aapl'):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
# Function to get stock data with aggregation
    def get_stock_data_from_db(self, start_date: str, end_date: str, aggregate: Optional[str] = 'monthly') -> List[dict]:
        # Validate and convert string date to datetime format
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")
        
        # Query to filter data within the date range
        data_cursor = self.collection.find({
            'Date': {'$gte': start, '$lte': end}
        })

        # Convert to DataFrame for aggregation
        data = pd.DataFrame(list(data_cursor))

        if data.empty:
            raise ValueError("No data found for the specified range")

        # Ensure the Date field is in datetime format
        if not pd.api.types.is_datetime64_any_dtype(data['Date']):
            data['Date'] = pd.to_datetime(data['Date'])

        # Aggregation based on month or year
        if aggregate == 'monthly':
            data['Month'] = data['Date'].dt.to_period('M')
            aggregated_data = data.groupby('Month').agg({'Close': 'mean'}).reset_index()
            aggregated_data['Month'] = aggregated_data['Month'].astype(str)
            result = [{"date": row['Month'], "avg_close": row['Close']} for _, row in aggregated_data.iterrows()]
        elif aggregate == 'yearly':
            data['Year'] = data['Date'].dt.year
            aggregated_data = data.groupby('Year').agg({'Close': 'mean'}).reset_index()
            result = [{"date": str(row['Year']), "avg_close": row['Close']} for _, row in aggregated_data.iterrows()]
        else:
            raise ValueError("Invalid aggregate parameter. Please choose 'monthly' or 'yearly'.")
        
        return result