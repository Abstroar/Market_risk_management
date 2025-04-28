# Python Backend

This is a FastAPI-based backend for the login application.

## Setup

1. Make sure you have Python 3.8+ installed
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

1. Make sure MongoDB is running locally on port 27017
2. Start the server:
   ```bash
   python server.py
   ```
   or
   ```bash
   uvicorn server:app --reload
   ```

The server will run on http://localhost:5000

## API Endpoints

- POST `/api/register` - Register a new user
- POST `/api/login` - Login with existing credentials

Both endpoints expect JSON data with `email` and `password` fields. 