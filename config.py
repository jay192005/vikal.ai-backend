"""
Configuration file for GDP Growth Prediction Model
Ensures consistency across training and deployment
"""

# Data paths
DATASET_PATH = "final_data_with_year.csv"

# Model paths
MODEL_PATH = "gdp_model.pkl"
ENCODER_PATH = "country_encoder.pkl"

# Feature columns (for reference)
FEATURE_COLUMNS = [
    'Country_Encoded',
    'Population_Growth_Rate_Lag1',
    'Exports_Growth_Rate_Lag1',
    'Imports_Growth_Rate_Lag1',
    'Investment_Growth_Rate_Lag1',
    'Consumption_Growth_Rate_Lag1',
    'Govt_Spend_Growth_Rate_Lag1'
]

TARGET_COLUMN = 'GDP_Growth_Rate'

# Temporal split year (train on data before this year, test on this year onwards)
TEMPORAL_SPLIT_YEAR = 2019

# Model hyperparameters
MODEL_PARAMS = {
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42,
    'n_jobs': -1
}
