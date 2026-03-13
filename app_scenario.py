"""
GDP Economic Scenario Simulator API
Sensitivity analysis and policy simulation tool

Purpose: Simulate economic scenarios and test policy impacts
Example: "If exports grow 10% and investment grows 5%, what happens to GDP?"

This is NOT a forecasting tool - it's a scenario simulator!
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import traceback

from config import DATASET_PATH
from firebase_auth import initialize_firebase_auth, require_auth

app = Flask(__name__)

# Configure CORS for development and production
# Allow requests from local development and Firebase Hosting
allowed_origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative dev port
    "https://gdp-grow-prediction-model.web.app",  # Firebase Hosting
    "https://gdp-grow-prediction-model.firebaseapp.com",  # Firebase Hosting alternative
]

# In production, you might want to add your custom domain
# allowed_origins.append("https://your-custom-domain.com")

CORS(app, origins=allowed_origins, supports_credentials=True)

# Global variables
model = None
encoder = None
feature_info = None
df_history = None

# Initialize Firebase Authentication
initialize_firebase_auth()


def load_model_and_data():
    """Load scenario model, encoder, and historical data"""
    global model, encoder, feature_info, df_history
    
    # Load Scenario Model & Encoder
    try:
        import os
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        model_path = os.path.join(script_dir, "gdp_scenario_model.pkl")
        encoder_path = os.path.join(script_dir, "country_encoder_scenario.pkl")
        feature_path = os.path.join(script_dir, "feature_info_scenario.pkl")
        
        # Check if files exist
        if not os.path.exists(model_path):
            print(f"⚠️ Model file not found at: {model_path}")
            model = None
        else:
            model = joblib.load(model_path)
            print(f"✅ Scenario Model loaded from {model_path}")
        
        if not os.path.exists(encoder_path):
            print(f"⚠️ Encoder file not found at: {encoder_path}")
            encoder = None
        else:
            encoder = joblib.load(encoder_path)
            print(f"✅ Encoder loaded from {encoder_path}")
            print(f"   Number of countries: {len(encoder.classes_)}")
        
        if not os.path.exists(feature_path):
            print(f"⚠️ Feature info file not found at: {feature_path}")
            feature_info = None
        else:
            feature_info = joblib.load(feature_path)
            print(f"✅ Feature info loaded from {feature_path}")
            
    except Exception as e:
        print(f"⚠️ Error loading model/encoder: {e}")
        print(f"⚠️ Current working directory: {os.getcwd()}")
        print(f"⚠️ Script directory: {script_dir}")
        import traceback
        traceback.print_exc()
        model = None
        encoder = None
        feature_info = None
    
    # Load Historical Data
    try:
        df_history = pd.read_csv(DATASET_PATH)
        df_history = df_history[[
            'Country', 'Year', 'GDP_Growth_Rate',
            'Exports of goods and services_Growth_Rate',
            'Imports of goods and services_Growth_Rate'
        ]]
        df_history.columns = [
            'Country', 'Year', 'GDP_Growth', 
            'Exports_Growth', 'Imports_Growth'
        ]
        print(f"✅ Historical data loaded")
        print(f"   Countries: {df_history['Country'].nunique()}")
        print(f"   Years: {df_history['Year'].min()} - {df_history['Year'].max()}")
    except Exception as e:
        print(f"⚠️ Historical Data Error: {e}")
        df_history = pd.DataFrame()


# Load on startup
load_model_and_data()


@app.route('/')
def home():
    """API information"""
    return jsonify({
        'name': 'Vikalp.ai - GDP Economic Scenario Simulator',
        'version': 'v4.0-scenario',
        'purpose': 'Sensitivity Analysis & Policy Simulation',
        'description': 'Simulate economic scenarios and test policy impacts',
        'model_type': 'Concurrent Indicators (Same Year)',
        'use_case': 'What-if analysis, not forecasting',
        'example': 'If exports grow 10% and investment grows 5%, what happens to GDP?',
        'model_loaded': model is not None,
        'encoder_loaded': encoder is not None,
        'data_loaded': not df_history.empty if df_history is not None else False,
        'endpoints': {
            '/': 'GET - API information',
            '/api/countries': 'GET - List all countries',
            '/api/history': 'GET - Historical data for a country',
            '/simulate': 'POST - Simulate economic scenario'
        }
    })


@app.route('/api/countries', methods=['GET'])
def get_countries():
    """Get list of all available countries"""
    try:
        if df_history is None or df_history.empty:
            return jsonify({'error': 'Historical data not available'}), 500
        
        countries = sorted(df_history['Country'].unique().tolist())
        return jsonify(countries)
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve countries', 'details': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get historical GDP data for a specific country"""
    try:
        country = request.args.get('country')
        
        if not country:
            return jsonify({'error': 'Missing required parameter: country'}), 400
        
        if df_history is None or df_history.empty:
            return jsonify({'error': 'Historical data not available'}), 500
        
        country_data = df_history[df_history['Country'] == country].sort_values('Year')
        
        if country_data.empty:
            return jsonify({'error': f'No data found for country: {country}'}), 404
        
        data_json = country_data.replace({np.nan: None}).to_dict(orient='records')
        return jsonify(data_json)
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve historical data', 'details': str(e)}), 500


def validate_scenario_input(data):
    """
    Validate incoming scenario simulation request
    
    Returns: (is_valid, error_message, validated_data)
    """
    required_fields = [
        'Country',
        'Population_Growth_Rate',
        'Exports_Growth_Rate',
        'Imports_Growth_Rate',
        'Investment_Growth_Rate',
        'Consumption_Growth_Rate',
        'Govt_Spend_Growth_Rate'
    ]
    
    # Check if data exists
    if not data:
        return False, 'Request body is empty', None
    
    # Check for missing fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f'Missing required fields: {", ".join(missing_fields)}', None
    
    validated_data = {}
    
    # Validate country
    try:
        validated_data['Country'] = str(data['Country']).strip()
        if not validated_data['Country']:
            return False, 'Country name cannot be empty', None
    except Exception:
        return False, 'Invalid Country value', None
    
    # Validate numeric fields
    numeric_fields = [
        'Population_Growth_Rate',
        'Exports_Growth_Rate',
        'Imports_Growth_Rate',
        'Investment_Growth_Rate',
        'Consumption_Growth_Rate',
        'Govt_Spend_Growth_Rate'
    ]
    
    for field in numeric_fields:
        try:
            value = float(data[field])
            
            # Check for reasonable ranges (-100% to +100%)
            if not -100 <= value <= 100:
                return False, f'{field} value {value} is outside reasonable range (-100 to 100)', None
            
            validated_data[field] = value
        except (ValueError, TypeError):
            return False, f'Invalid {field} value: must be a number', None
    
    return True, None, validated_data


@app.route('/simulate', methods=['POST'])
def simulate_scenario():
    """
    Simulate economic scenario
    
    Expected JSON body:
    {
        "Country": "United States",
        "Population_Growth_Rate": 1.0,
        "Exports_Growth_Rate": 10.0,
        "Imports_Growth_Rate": 5.0,
        "Investment_Growth_Rate": 8.0,
        "Consumption_Growth_Rate": 3.0,
        "Govt_Spend_Growth_Rate": 2.0
    }
    
    Returns predicted GDP growth rate for this scenario
    """
    try:
        # Get JSON data
        data = request.get_json()
        
        # Validate input
        is_valid, error_msg, validated_data = validate_scenario_input(data)
        
        if not is_valid:
            return jsonify({
                'error': 'Invalid input',
                'message': error_msg,
                'required_fields': [
                    'Country',
                    'Population_Growth_Rate',
                    'Exports_Growth_Rate',
                    'Imports_Growth_Rate',
                    'Investment_Growth_Rate',
                    'Consumption_Growth_Rate',
                    'Govt_Spend_Growth_Rate'
                ],
                'example': {
                    'Country': 'United States',
                    'Population_Growth_Rate': 1.0,
                    'Exports_Growth_Rate': 10.0,
                    'Imports_Growth_Rate': 5.0,
                    'Investment_Growth_Rate': 8.0,
                    'Consumption_Growth_Rate': 3.0,
                    'Govt_Spend_Growth_Rate': 2.0
                }
            }), 400
        
        # Check if model is loaded
        if model is None or encoder is None:
            return jsonify({
                'error': 'Model not loaded',
                'message': 'Scenario model is not available. Please train the model first.'
            }), 500
        
        # Check if country is in encoder
        try:
            country_code = encoder.transform([validated_data['Country']])[0]
        except ValueError:
            return jsonify({
                'error': 'Unknown country',
                'message': f"Country '{validated_data['Country']}' not found in training data",
                'available_countries': encoder.classes_.tolist()[:10]
            }), 400
        
        # Prepare features (CURRENT YEAR - no lagging)
        features = [
            country_code,
            validated_data['Population_Growth_Rate'],
            validated_data['Exports_Growth_Rate'],
            validated_data['Imports_Growth_Rate'],
            validated_data['Investment_Growth_Rate'],
            validated_data['Consumption_Growth_Rate'],
            validated_data['Govt_Spend_Growth_Rate']
        ]
        
        # Make prediction
        predicted_gdp = model.predict([features])[0]
        
        return jsonify({
            'scenario': {
                'country': validated_data['Country'],
                'population_growth': validated_data['Population_Growth_Rate'],
                'exports_growth': validated_data['Exports_Growth_Rate'],
                'imports_growth': validated_data['Imports_Growth_Rate'],
                'investment_growth': validated_data['Investment_Growth_Rate'],
                'consumption_growth': validated_data['Consumption_Growth_Rate'],
                'govt_spend_growth': validated_data['Govt_Spend_Growth_Rate']
            },
            'predicted_gdp_growth': round(predicted_gdp, 2),
            'model_type': 'Scenario Simulator (Concurrent Indicators)',
            'interpretation': f'If these growth rates occur simultaneously, GDP is predicted to grow by {round(predicted_gdp, 2)}%',
            'note': 'This is a sensitivity analysis tool, not a forecast'
        })
    
    except Exception as e:
        # Log full error for debugging
        print(f"❌ Simulation Error: {e}")
        print(traceback.format_exc())
        
        return jsonify({
            'error': 'Simulation failed',
            'message': 'An unexpected error occurred during simulation',
            'details': str(e)
        }), 500


@app.route('/api/baseline', methods=['GET'])
def get_baseline():
    """
    Get baseline (average) growth rates for a country
    Useful for creating scenarios
    """
    try:
        country = request.args.get('country')
        
        if not country:
            return jsonify({'error': 'Missing required parameter: country'}), 400
        
        # Load full dataset
        df = pd.read_csv(DATASET_PATH)
        country_data = df[df['Country'] == country]
        
        if country_data.empty:
            return jsonify({'error': f'No data found for country: {country}'}), 404
        
        # Calculate average growth rates
        baseline = {
            'country': country,
            'baseline_rates': {
                'population': round(country_data['Population_Growth_Rate'].mean(), 2),
                'exports': round(country_data['Exports of goods and services_Growth_Rate'].mean(), 2),
                'imports': round(country_data['Imports of goods and services_Growth_Rate'].mean(), 2),
                'investment': round(country_data['Gross capital formation_Growth_Rate'].mean(), 2),
                'consumption': round(country_data['Final consumption expenditure_Growth_Rate'].mean(), 2),
                'govt_spend': round(country_data['Government_Expenditure_Growth_Rate'].mean(), 2)
            },
            'note': 'These are historical averages. Use as baseline for scenario simulations.'
        }
        
        return jsonify(baseline)
    
    except Exception as e:
        return jsonify({'error': 'Failed to calculate baseline', 'details': str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': [
            '/', '/api/countries', '/api/history', '/simulate', '/api/baseline'
        ]
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred on the server'
    }), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
