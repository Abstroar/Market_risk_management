from pymongo import MongoClient
import pandas as pd
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class StockDataResponse(BaseModel):
    date: str
    avg_close: float


class StockDataService:
    def __init__(self,
                 db_uri: str = "mongodb+srv://abhilaksh:DVH1RDrl4DBUTCaA@capstone.vwbejki.mongodb.net/?retryWrites=true&w=majority&appName=Capstone",
                 db_name: str = 'stock_database', collection_name: str = 'amzn'):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_stock_data_from_db(self, start_date: str, end_date: str, aggregate: Optional[str] = 'monthly') -> List[
        dict]:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

        # Query and convert to DataFrame
        data_list = list(self.collection.find({
            'Date': {'$gte': start, '$lte': end}
        }))
        print(f"Fetched {len(data_list)} records from the database.")

        if not data_list:
            raise ValueError("No data found for the specified range")

        data = pd.DataFrame(data_list)

        # Ensure 'Date' is datetime
        if not pd.api.types.is_datetime64_any_dtype(data['Date']):
            data['Date'] = pd.to_datetime(data['Date'])

        # Handle aggregation
        if aggregate == 'daily':
            data['Day'] = data['Date'].dt.date
            aggregated_data = data.groupby('Day').agg({'Close': 'mean'}).reset_index()
            aggregated_data['Day'] = aggregated_data['Day'].astype(str)
            result = [{"date": row['Day'], "avg_close": row['Close']} for _, row in aggregated_data.iterrows()]

        elif aggregate == 'weekly':
            data['Week'] = data['Date'].dt.to_period('W').apply(lambda r: r.start_time)
            aggregated_data = data.groupby('Week').agg({'Close': 'mean'}).reset_index()
            aggregated_data['Week'] = aggregated_data['Week'].dt.strftime('%Y-%m-%d')
            result = [{"date": row['Week'], "avg_close": row['Close']} for _, row in aggregated_data.iterrows()]

        elif aggregate == 'monthly':
            data['Month'] = data['Date'].dt.to_period('M')
            aggregated_data = data.groupby('Month').agg({'Close': 'mean'}).reset_index()
            aggregated_data['Month'] = aggregated_data['Month'].astype(str)
            result = [{"date": row['Month'], "avg_close": row['Close']} for _, row in aggregated_data.iterrows()]

        elif aggregate == 'yearly':
            data['Year'] = data['Date'].dt.year
            aggregated_data = data.groupby('Year').agg({'Close': 'mean'}).reset_index()
            result = [{"date": str(row['Year']), "avg_close": row['Close']} for _, row in aggregated_data.iterrows()]

        else:
            raise ValueError("Invalid aggregate parameter. Choose from 'daily', 'weekly', 'monthly', or 'yearly'.")

        print(f"Aggregated data: {result}")
        return result

# Example call
# if __name__ == "__main__":
#     service = StockDataService()
#     print(service.get_stock_data_from_db("2022-05-02", "2024-06-29", aggregate="yearly"))
