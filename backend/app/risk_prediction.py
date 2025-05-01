import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from datetime import datetime, timedelta
import logging
from sklearn.preprocessing import MinMaxScaler
import os

logger = logging.getLogger(__name__)

class RiskPredictionService:
    def __init__(self, model_path='model_try/lstm_risk_model.h5'):
        try:
            # Get the absolute path to the model
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_abs_path = os.path.join(current_dir, model_path)
            
            if not os.path.exists(model_abs_path):
                raise FileNotFoundError(f"Model file not found at: {model_abs_path}")
                
            self.model = load_model(model_abs_path)
            logger.info(f"Successfully loaded LSTM risk prediction model from {model_abs_path}")
        except Exception as e:
            logger.error(f"Failed to load LSTM risk prediction model: {str(e)}")
            raise

    def prepare_data(self, time_series_data):
        """Prepare time series data for the LSTM model"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(time_series_data)
            
            # Calculate returns
            df['returns'] = df['current_price'].pct_change()
            
            # Calculate rolling volatility (60-day window)
            window_size = 60
            df['volatility'] = df['returns'].rolling(window=window_size).std()
            
            # Drop NaN values
            df = df.dropna()
            
            if len(df) < window_size:
                raise ValueError("Not enough data points for prediction")
            
            # Normalize volatility
            scaler = MinMaxScaler()
            scaled_volatility = scaler.fit_transform(df['volatility'].values.reshape(-1, 1))
            
            # Prepare input data for LSTM
            x = []
            for i in range(window_size, len(scaled_volatility)):
                x.append(scaled_volatility[i-window_size:i, 0])
            
            return np.array(x).reshape(-1, window_size, 1)
            
        except Exception as e:
            logger.error(f"Error preparing data for risk prediction: {str(e)}")
            raise

    def predict_risk(self, time_series_data):
        """Predict risk level based on time series data using LSTM model"""
        try:
            # Prepare data
            x = self.prepare_data(time_series_data)
            
            # Make prediction
            prediction = self.model.predict(x)
            
            # Get the latest prediction
            latest_prediction = prediction[-1][0]
            
            # Convert to risk level (0-100)
            risk_level = int(latest_prediction * 100)
            
            # Determine risk category
            if risk_level < 30:
                risk_category = "Low"
            elif risk_level < 70:
                risk_category = "Medium"
            else:
                risk_category = "High"
            
            return {
                "risk_level": risk_level,
                "risk_category": risk_category,
                "confidence": float(prediction[-1][0]),
                "model_type": "LSTM"
            }
            
        except Exception as e:
            logger.error(f"Error predicting risk: {str(e)}")
            raise 