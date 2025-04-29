import yfinance as yf
import pandas as pd
from pymongo import MongoClient

client = MongoClient("mongodb+srv://abhilaksh:DVH1RDrl4DBUTCaA@capstone.vwbejki.mongodb.net/?retryWrites=true&w=majority&appName=Capstone")
db = client["stock_database"]
# collection = db["stock_data"]

# , "MSFT", "GOOG", "AMZN", "TSLA", "META", "NFLX", "NVDA"

# def large_uploader():
#     STOCK_SYMBOLS = ["AAPL"]
#     for i in STOCK_SYMBOLS:
#         collection = db[i.lower()]
#         data = yf.download(i, period='1y')
#         data.reset_index(inplace=True)
#         documents = data.to_dict(orient="records")
#         collection.insert_many(documents)
# large_uploader()
print("hii")


def upload_from_csv():
    collection = db["aapl"]

    data = pd.read_csv("D:/Capstone project/another/backend/app/AAPL.csv")  
    data['Date'] = pd.to_datetime(data['Date'], format="%Y-%m-%d")

    data.reset_index(drop=True, inplace=True)

    documents = data.to_dict(orient="records")

    if documents:
        collection.insert_many(documents)
        print(f"Saved {len(documents)} records from CSV.")
    else:
        print("CSV file is empty!")

upload_from_csv()
print("done")