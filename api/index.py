# Vercel Serverless Function Entry Point
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Set environment variable to indicate we're in Vercel
os.environ['VERCEL'] = '1'

# Import Flask app
from app_scenario import app

# Vercel will call this app
# No need for additional wrapper
