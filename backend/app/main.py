from fastapi import FastAPI, HTTPException, Query, Request, Depends, status
from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime, timedelta
import requests
import os
import time
import logging
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from .get_stock_data import StockDataResponse, StockDataService
from .home_data import *
from dotenv import load_dotenv
from .stock_fetcher import fetch_and_store_stock_data
from .stock_data import get_stock_data as get_twelvedata_stock_data
from .time_series_data import TimeSeriesDataService
from .risk_prediction import RiskPredictionService

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS setup (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow both Vite and React default ports
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
    max_age=3600,  # Cache preflight requests for 1 hour
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
    # Ensure collections exist
    if "users" not in db.list_collection_names():
        db.create_collection("users")
    if "portfolios" not in db.list_collection_names():
        db.create_collection("portfolios")
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

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")  # Move to .env later
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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
            
        logger.info(f"Received request for {symbol} from {start_date} to {end_date} with aggregation {aggregate}")
        service = StockDataService()
        data = service.get_stock_data_from_db(start_date, end_date, symbol, aggregate)
        logger.info(f"Returning {len(data)} data points")
        return {"data": data}
    except ValueError as e:
        logger.error(f"ValueError in get_stock_data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_stock_data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching stock data")

@app.post("/register")
async def register(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received registration data: {data}")
        
        # Map frontend fields to backend fields
        user_data = {
            "username": data.get("username", ""),
            "password": data.get("password", ""),
            "profile_image": data.get("profile_img", "https://www.kindpng.com/picc/m/722-7221920_placeholder-profile-image-placeholder-png-transparent-png.png"),
            "age": data.get("age"),
            "gender": data.get("gender")
        }
        
        # Validate required fields
        required_fields = ["username", "password"]
        missing_fields = [field for field in required_fields if not user_data[field]]
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Check if username already exists
        if db.users.find_one({"username": user_data["username"]}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Hash the password
        hashed_password = get_password_hash(user_data["password"])
        logger.info(f"Password hashed during registration: {hashed_password}")
        
        # Create user document
        user_dict = {
            "username": user_data["username"],
            "password": hashed_password,
            "profile_image": user_data["profile_image"],
            "age": user_data["age"],
            "gender": user_data["gender"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Insert user into database
        result = db.users.insert_one(user_dict)
        user_dict["id"] = str(result.inserted_id)
        
        # Create portfolio for new user
        portfolio = {
            "user_id": str(result.inserted_id),
            "symbols": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        db.portfolios.insert_one(portfolio)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_dict["username"]},
            expires_delta=access_token_expires
        )
        
        # Return user data with token
        return {
            "id": user_dict["id"],
            "username": user_dict["username"],
            "profile_image": user_dict["profile_image"],
            "age": user_dict["age"],
            "gender": user_dict["gender"],
            "created_at": user_dict["created_at"],
            "updated_at": user_dict["updated_at"],
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException as he:
        logger.error(f"HTTP Exception in register endpoint: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Error in register endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/login")
async def login_endpoint(request: Request):
    try:
        data = await request.json()
        logger.info(f"Login attempt with data: {data}")
        
        # Create form data for token endpoint
        form_data = OAuth2PasswordRequestForm(
            username=data.get("username", ""),
            password=data.get("password", ""),
            grant_type="password",
            scope="",
            client_id="",
            client_secret=""
        )
        
        # Call the token endpoint
        return await login(form_data)
    except Exception as e:
        logger.error(f"Error in login endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        logger.info(f"Token request for username: {form_data.username}")
        user = db.users.find_one({"username": form_data.username})
        
        if not user:
            logger.error(f"User not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Found user, stored password hash: {user['password']}")
        logger.info(f"Attempting to verify password for user: {form_data.username}")
        
        if not verify_password(form_data.password, user["password"]):
            logger.error("Password verification failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info("Password verified successfully")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error in token endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    user = db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

# Portfolio endpoints
@app.get("/portfolio")
async def get_portfolio(current_user: dict = Depends(get_current_user)):
    portfolio = db.portfolios.find_one({"user_id": str(current_user["_id"])})
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

@app.put("/portfolio")
async def update_portfolio(symbols: List[str], current_user: dict = Depends(get_current_user)):
    portfolio = db.portfolios.find_one({"user_id": str(current_user["_id"])})
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    db.portfolios.update_one(
        {"user_id": str(current_user["_id"])},
        {"$set": {"symbols": symbols, "updated_at": datetime.now()}}
    )
    return {"message": "Portfolio updated successfully"}

# Initialize services
time_series_service = TimeSeriesDataService()
risk_prediction_service = RiskPredictionService()

@app.get("/api/fetch-stock/{symbol}")
async def fetch_stock(symbol: str):
    try:
        # Try to get data from TwelveData
        try:
            current_data = get_twelvedata_stock_data(symbol)
        except HTTPException as e:
            if e.status_code == 404:
                return {"status": "error", "message": f"Stock {symbol} not found"}
            return {"status": "error", "message": "Failed to fetch stock data"}
        except Exception as e:
            print(f"Error fetching from TwelveData: {str(e)}")
            return {"status": "error", "message": "Failed to fetch stock data"}
            
        # Create data point for current data
        data_point = {
            "symbol": symbol.upper(),
            "date": current_data["date"].strftime("%Y-%m-%dT%H:%M:%S.000+00:00"),
            "current_price": str(current_data["current_price"]),
            "open_price": str(current_data["open_price"]),
            "high_price": str(current_data["high_price"]),
            "low_price": str(current_data["low_price"]),
            "volume": str(current_data["volume"])
        }
        
        # Store in database
        time_series_service.collection.insert_one(data_point)
        
        # Remove _id from response
        data_point.pop("_id", None)
        
        return {
            "status": "success",
            "data": data_point
        }
                
    except Exception as e:
        print(f"Error in fetch_stock: {str(e)}")
        return {"status": "error", "message": "Internal server error"}

@app.get("/api/stock-data")
async def get_stock_data_range(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    try:
        # Get time series data from the database
        data = time_series_service.get_time_series_data(symbol, start_date, end_date)
        
        if not data:
            return {"status": "success", "data": []}
            
        return {"status": "success", "data": data}
        
    except Exception as e:
        print(f"Error in get_stock_data_range: {str(e)}")
        return {"status": "error", "message": "Internal server error"}

@app.get("/api/risk-prediction/{symbol}")
async def get_risk_prediction(symbol: str):
    try:
        # Get time series data for the last 90 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        time_series_data = time_series_service.get_time_series_data(
            symbol,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        if not time_series_data:
            return {
                "status": "error",
                "message": "Not enough historical data for risk prediction"
            }
        
        # Get risk prediction
        risk_prediction = risk_prediction_service.predict_risk(time_series_data)
        
        return {
            "status": "success",
            "data": risk_prediction
        }
        
    except Exception as e:
        print(f"Error in get_risk_prediction: {str(e)}")
        return {"status": "error", "message": "Internal server error"}

@app.get("/api/available-symbols")
async def get_available_symbols():
    try:
        symbols = time_series_service.get_available_symbols()
        return {"status": "success", "data": symbols}
    except Exception as e:
        print(f"Error in get_available_symbols: {str(e)}")
        return {"status": "error", "message": "Internal server error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)