from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["risk_db"]
collection = db["application_data"]

def insert_data(data):
    """Insert a document into the MongoDB collection."""
    collection.insert_one(data)

def fetch_all_data():
    """Fetch all documents from the MongoDB collection."""
    return list(collection.find({}, {"_id": 0}))
