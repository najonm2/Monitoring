"""
Base Agent Class
================

Abstract base class for all AI agents in the system.
Provides common functionality for ML operations, logging, and state management.
"""

import logging
import pickle
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from .config import MODELS_DIR, LOGS_DIR, LOGGING_CONFIG


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    
    Provides:
    - Model persistence (save/load)
    - Logging infrastructure
    - State management
    - Common data processing utilities
    """
    
    def __init__(self, agent_name: str):
        """
        Initialize base agent.
        
        Args:
            agent_name: Unique identifier for this agent
        """
        self.agent_name = agent_name
        self.model = None
        self.is_trained = False
        self.last_trained = None
        self.model_path = MODELS_DIR / f'{agent_name}_model.pkl'
        
        # Setup logging
        self.logger = self._setup_logger()
        self.logger.info(f"Initialized {agent_name}")
        
    def _setup_logger(self) -> logging.Logger:
        """Configure logger for this agent."""
        logger = logging.getLogger(self.agent_name)
        logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))
        
        # File handler
        fh = logging.FileHandler(LOGGING_CONFIG['file'])
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(LOGGING_CONFIG['format'])
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    @abstractmethod
    def train(self, data: pd.DataFrame) -> None:
        """
        Train the agent's model on historical data.
        
        Args:
            data: Training dataset
        """
        pass
    
    @abstractmethod
    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Make predictions on new data.
        
        Args:
            data: Input data for prediction
            
        Returns:
            DataFrame with predictions and confidence scores
        """
        pass
    
    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform analysis and generate insights.
        
        Args:
            data: Data to analyze
            
        Returns:
            Dictionary containing analysis results and insights
        """
        pass
    
    def save_model(self) -> bool:
        """
        Persist the trained model to disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            model_data = {
                'model': self.model,
                'is_trained': self.is_trained,
                'last_trained': self.last_trained,
                'agent_name': self.agent_name,
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            self.logger.info(f"Model saved to {self.model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save model: {str(e)}")
            return False
    
    def load_model(self) -> bool:
        """
        Load a previously trained model from disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.model_path.exists():
                self.logger.warning(f"No saved model found at {self.model_path}")
                return False
            
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.is_trained = model_data['is_trained']
            self.last_trained = model_data['last_trained']
            
            self.logger.info(f"Model loaded from {self.model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            return False
    
    def needs_retraining(self, retrain_days: int = 7) -> bool:
        """
        Check if model needs retraining based on age.
        
        Args:
            retrain_days: Number of days before retraining is needed
            
        Returns:
            True if retraining is needed
        """
        if not self.is_trained or self.last_trained is None:
            return True
        
        age = datetime.now() - self.last_trained
        return age > timedelta(days=retrain_days)
    
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Common preprocessing steps for all agents.
        
        Args:
            data: Raw input data
            
        Returns:
            Preprocessed data
        """
        df = data.copy()
        
        # Convert datetime columns
        datetime_cols = df.select_dtypes(include=['object']).columns
        for col in datetime_cols:
            try:
                df[col] = pd.to_datetime(df[col], errors='ignore')
            except:
                pass
        
        # Handle missing values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        
        return df
    
    def extract_temporal_features(self, df: pd.DataFrame, 
                                   datetime_col: str = 'start_time') -> pd.DataFrame:
        """
        Extract temporal features from datetime column.
        
        Args:
            df: DataFrame with datetime column
            datetime_col: Name of datetime column
            
        Returns:
            DataFrame with added temporal features
        """
        if datetime_col not in df.columns:
            return df
        
        df = df.copy()
        dt = pd.to_datetime(df[datetime_col])
        
        df['hour_of_day'] = dt.dt.hour
        df['day_of_week'] = dt.dt.dayofweek
        df['day_of_month'] = dt.dt.day
        df['month'] = dt.dt.month
        df['is_weekend'] = (dt.dt.dayofweek >= 5).astype(int)
        df['is_business_hours'] = ((dt.dt.hour >= 8) & (dt.dt.hour < 18)).astype(int)
        
        return df
    
    def calculate_rolling_stats(self, df: pd.DataFrame, 
                                 value_col: str,
                                 windows: List[int] = [24, 168]) -> pd.DataFrame:
        """
        Calculate rolling statistics for a numeric column.
        
        Args:
            df: Input DataFrame
            value_col: Column to calculate statistics for
            windows: List of window sizes (in hours)
            
        Returns:
            DataFrame with added rolling statistics
        """
        df = df.copy()
        
        for window in windows:
            df[f'{value_col}_rolling_mean_{window}h'] = (
                df[value_col].rolling(window=window, min_periods=1).mean()
            )
            df[f'{value_col}_rolling_std_{window}h'] = (
                df[value_col].rolling(window=window, min_periods=1).std()
            )
            df[f'{value_col}_rolling_min_{window}h'] = (
                df[value_col].rolling(window=window, min_periods=1).min()
            )
            df[f'{value_col}_rolling_max_{window}h'] = (
                df[value_col].rolling(window=window, min_periods=1).max()
            )
        
        return df
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the agent.
        
        Returns:
            Dictionary with agent status information
        """
        return {
            'agent_name': self.agent_name,
            'is_trained': self.is_trained,
            'last_trained': self.last_trained.isoformat() if self.last_trained else None,
            'needs_retraining': self.needs_retraining(),
            'model_exists': self.model_path.exists(),
        }
