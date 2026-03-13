# Vercel Serverless Function Entry Point
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
from app_scenario import app

# Export the app for Vercel
# Vercel will automatically handle WSGI
handler = app
