"""
AI System Configuration
========================

Configuration settings for ML models, agents, and AI processing.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / 'models'
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Model configurations
ANOMALY_DETECTION_CONFIG = {
    'isolation_forest': {
        'contamination': 0.1,  # Expected proportion of outliers
        'n_estimators': 100,
        'max_samples': 256,
        'random_state': 42,
    },
    'lstm': {
        'sequence_length': 24,  # Hours of history to consider
        'hidden_units': 64,
        'dropout': 0.2,
        'epochs': 50,
        'batch_size': 32,
    },
}

PREDICTIVE_FAILURE_CONFIG = {
    'random_forest': {
        'n_estimators': 200,
        'max_depth': 20,
        'min_samples_split': 5,
        'random_state': 42,
    },
    'gradient_boosting': {
        'n_estimators': 100,
        'learning_rate': 0.1,
        'max_depth': 5,
        'random_state': 42,
    },
    'threshold': 0.7,  # Probability threshold for failure prediction
}

PATTERN_IDENTIFICATION_CONFIG = {
    'kmeans': {
        'n_clusters': 5,
        'random_state': 42,
        'max_iter': 300,
    },
    'dbscan': {
        'eps': 0.5,
        'min_samples': 5,
    },
    'time_series': {
        'seasonal_period': 24,  # Hours in a day
        'trend_window': 168,    # Hours in a week
    },
}

ALERT_RECOMMENDER_CONFIG = {
    'priority_weights': {
        'failure_probability': 0.4,
        'runtime_deviation': 0.3,
        'historical_failures': 0.2,
        'business_impact': 0.1,
    },
    'alert_thresholds': {
        'critical': 0.8,
        'high': 0.6,
        'medium': 0.4,
        'low': 0.2,
    },
}

# Feature engineering settings
FEATURE_CONFIG = {
    'runtime_features': [
        'duration_seconds',
        'hour_of_day',
        'day_of_week',
        'is_weekend',
        'is_business_hours',
    ],
    'statistical_features': [
        'rolling_mean_24h',
        'rolling_std_24h',
        'rolling_mean_7d',
        'rolling_std_7d',
    ],
    'historical_features': [
        'failure_count_24h',
        'failure_count_7d',
        'success_rate_24h',
        'avg_duration_7d',
    ],
}

# Agent execution settings
EXECUTION_CONFIG = {
    'batch_size': 1000,  # Records to process at once
    'lookback_days': 90,  # Historical data to consider
    'update_frequency_minutes': 15,  # How often to run agents
    'model_retrain_days': 7,  # Retrain models every N days
}

# Logging settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': LOGS_DIR / 'ai_system.log',
}
