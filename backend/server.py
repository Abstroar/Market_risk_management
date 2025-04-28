from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Login API",
    description="A simple login and registration API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
try:
    client = MongoClient("mongodb://localhost:27017")
    db = client["login-app"]
    users_collection = db["users"]
    print("Successfully connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

# Pydantic models for request/response validation
class User(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    message: str

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Login API",
        "endpoints": {
            "register": "/api/register",
            "login": "/api/login"
        }
    }

@app.post("/api/register", response_model=UserResponse)
async def register(user: User):
    try:
        # Check if user already exists
        if users_collection.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        users_collection.insert_one(user.dict())
        return {"message": "You are registered successfully. Please go to login page."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login", response_model=UserResponse)
async def login(user: User):
    try:
        # Find user in database
        found_user = users_collection.find_one({
            "email": user.email,
            "password": user.password
        })
        
        if found_user:
            return {"message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000) 