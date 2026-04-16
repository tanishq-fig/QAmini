"""
Vercel serverless function handler for QAMini FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# For Vercel cold start optimization, we'll use a lightweight approach
# This file acts as the entry point for all API requests

# Try to import from local backend, fall back to importing modules directly
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Create a minimal app for Vercel
# Note: For production, you may want to use a separate backend service
app = FastAPI(title="QAMini API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "QAMini API is running on Vercel"}

@app.get("/")
async def root():
    return {"message": "QAMini API - Backend running on Vercel"}

# NOTE: For full functionality with data analysis and chat features:
# 1. Deploy backend separately to Railway, Heroku, or similar
# 2. Update frontend API_BASE URL in App.jsx to point to the backend service
# 3. Or use Vercel Functions to serve the entire FastAPI backend
