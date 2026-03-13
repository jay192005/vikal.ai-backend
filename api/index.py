# Vercel Serverless Function Entry Point
# This file is required for Vercel to recognize the Python backend

import sys
import os

# Add parent directory to path to import app_scenario
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_scenario import app

# Vercel will call this handler
def handler(event, context):
    """
    Vercel serverless function handler
    """
    return app

# For Vercel, we need to export the Flask app
# Vercel will handle the WSGI interface
app = app
