"""
Feature Engineering Pipeline
==============================

Centralized feature engineering for all AI agents.
Transforms raw job data into ML-ready features.
"""

from datetime import datetime, timedelta
from typing import List, Tuple
import pandas as pd
import numpy as np


class FeatureEngineer:
    """
    Feature engineering pipeline for job execution data.
    """
    
    def __init__(self):
        self.feature_catalog = {}
        
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature transformations to raw data.
        
        Args:
            df: Raw job execution data
            
        Returns:
            DataFrame with engineered features
        """
        df = df.copy()
        
        # Ensure datetime columns
        df = self._ensure_datetime_columns(df)
        
        # Temporal features
        df = self._add_temporal_features(df)
        
        # Runtime features
        df = self._add_runtime_features(df)
        
        # Historical features
        df = self._add_historical_features(df)
        
        # Statistical features
        df = self._add_statistical_features(df)
        
        # Business context features
        df = self._add_business_features(df)
        
        # Update feature catalog
        self._update_catalog(df)
        
        return df
    
    def _ensure_datetime_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert datetime columns to proper format."""
        datetime_candidates = ['start_time', 'end_time', 'last_run_time']
        
        for col in datetime_candidates:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
        
        return df
    
    def _add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features."""
        if 'start_time' not in df.columns:
            return df
        
        dt = pd.to_datetime(df['start_time'])
        
        # Basic temporal
        df['year'] = dt.dt.year
        df['month'] = dt.dt.month
        df['day'] = dt.dt.day
        df['hour_of_day'] = dt.dt.hour
        df['day_of_week'] = dt.dt.dayofweek
        df['day_of_month'] = dt.dt.day
        df['week_of_year'] = dt.dt.isocalendar().week
        
        # Binary temporal flags
        df['is_weekend'] = (dt.dt.dayofweek >= 5).astype(int)
        df['is_monday'] = (dt.dt.dayofweek == 0).astype(int)
        df['is_friday'] = (dt.dt.dayofweek == 4).astype(int)
        df['is_month_start'] = (dt.dt.day <= 5).astype(int)
        df['is_month_end'] = (dt.dt.day >= 25).astype(int)
        
        # Business hours (8 AM - 6 PM)
        df['is_business_hours'] = ((dt.dt.hour >= 8) & (dt.dt.hour < 18)).astype(int)
        
        # Shift classification
        df['shift'] = pd.cut(
            dt.dt.hour,
            bins=[-1, 6, 14, 22, 24],
            labels=['night', 'morning', 'afternoon', 'evening']
        )
        
        # Cyclical encoding for hour and day
        df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        return df
    
    def _add_runtime_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add runtime-related features."""
        if 'duration_seconds' not in df.columns:
            return df
        
        # Duration conversions
        df['duration_minutes'] = df['duration_seconds'] / 60
        df['duration_hours'] = df['duration_seconds'] / 3600
        
        # Duration categories
        df['duration_category'] = pd.cut(
            df['duration_seconds'],
            bins=[0, 60, 300, 1800, 3600, 7200, float('inf')],
            labels=['very_quick', 'quick', 'normal', 'slow', 'very_slow', 'extremely_slow']
        )
        
        # Log transform for skewed distribution
        df['duration_log'] = np.log1p(df['duration_seconds'])
        
        # Per-job statistics (if job_name available)
        if 'job_name' in df.columns:
            job_stats = df.groupby('job_name')['duration_seconds'].agg([
                ('job_avg_duration', 'mean'),
                ('job_median_duration', 'median'),
                ('job_std_duration', 'std'),
                ('job_min_duration', 'min'),
                ('job_max_duration', 'max'),
            ]).reset_index()
            
            df = df.merge(job_stats, on='job_name', how='left')
            
            # Deviation from job average
            df['duration_deviation'] = (
                (df['duration_seconds'] - df['job_avg_duration']) / 
                df['job_std_duration'].replace(0, 1)
            )
            
            # Percentile rank within job
            df['duration_percentile'] = df.groupby('job_name')['duration_seconds'].rank(pct=True)
        
        return df
    
    def _add_historical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add features based on historical performance."""
        if 'start_time' not in df.columns or 'job_name' not in df.columns:
            return df
        
        # Sort by time
        df = df.sort_values('start_time')
        
        # Failure indicator
        if 'status' in df.columns:
            df['is_failure'] = (df['status'].isin(['FAILED', 'ERROR', 'ABORTED'])).astype(int)
            df['is_success'] = (df['status'] == 'SUCCESS').astype(int)
            
            # Historical failure counts
            df['failures_last_5'] = df.groupby('job_name')['is_failure'].rolling(5, min_periods=1).sum().reset_index(0, drop=True)
            df['failures_last_10'] = df.groupby('job_name')['is_failure'].rolling(10, min_periods=1).sum().reset_index(0, drop=True)
            df['failures_last_24h'] = df.groupby('job_name')['is_failure'].rolling(24, min_periods=1).sum().reset_index(0, drop=True)
            
            # Success rates
            df['success_rate_5'] = 1 - (df['failures_last_5'] / 5)
            df['success_rate_10'] = 1 - (df['failures_last_10'] / 10)
            df['success_rate_24h'] = 1 - (df['failures_last_24h'] / 24)
            
            # Consecutive failures
            df['consecutive_failures'] = (
                df.groupby('job_name')['is_failure']
                .apply(lambda x: x.groupby((x != x.shift()).cumsum()).cumsum())
                .reset_index(0, drop=True)
            )
            
            # Days since last failure
            df['last_failure_date'] = df[df['is_failure'] == 1].groupby('job_name')['start_time'].transform('max')
            df['days_since_failure'] = (df['start_time'] - df['last_failure_date']).dt.total_seconds() / 86400
        
        # Execution frequency
        df['executions_last_24h'] = df.groupby('job_name')['job_name'].transform(lambda x: x.rolling(24, min_periods=1).count())
        
        # Time since last run
        df['last_run_time'] = df.groupby('job_name')['start_time'].shift(1)
        df['hours_since_last_run'] = (df['start_time'] - df['last_run_time']).dt.total_seconds() / 3600
        
        return df
    
    def _add_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add statistical features."""
        if 'duration_seconds' not in df.columns:
            return df
        
        # Rolling statistics for duration
        windows = [5, 10, 24, 168]  # Last 5, 10, 24 hours, 1 week
        
        for window in windows:
            window_label = f'{window}h' if window <= 24 else f'{window//24}d'
            
            df[f'duration_rolling_mean_{window_label}'] = (
                df['duration_seconds'].rolling(window=window, min_periods=1).mean()
            )
            df[f'duration_rolling_std_{window_label}'] = (
                df['duration_seconds'].rolling(window=window, min_periods=1).std()
            )
            df[f'duration_rolling_min_{window_label}'] = (
                df['duration_seconds'].rolling(window=window, min_periods=1).min()
            )
            df[f'duration_rolling_max_{window_label}'] = (
                df['duration_seconds'].rolling(window=window, min_periods=1).max()
            )
            
            # Z-score within window
            mean = df[f'duration_rolling_mean_{window_label}']
            std = df[f'duration_rolling_std_{window_label}'].replace(0, 1)
            df[f'duration_zscore_{window_label}'] = (df['duration_seconds'] - mean) / std
        
        # Global statistics
        df['duration_global_zscore'] = (
            df['duration_seconds'] - df['duration_seconds'].mean()
        ) / df['duration_seconds'].std()
        
        # Exponential moving average
        df['duration_ema_short'] = df['duration_seconds'].ewm(span=5, adjust=False).mean()
        df['duration_ema_long'] = df['duration_seconds'].ewm(span=20, adjust=False).mean()
        
        return df
    
    def _add_business_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add business context features."""
        # Application/job categorization
        if 'job_name' in df.columns:
            # Extract application prefix (e.g., "LEVEL3", "MDM", "ERP")
            df['application'] = df['job_name'].str.extract(r'^([A-Z]+)', expand=False)
            
            # Job complexity indicator (based on name length as proxy)
            df['job_name_length'] = df['job_name'].str.len()
            df['job_complexity'] = pd.cut(
                df['job_name_length'],
                bins=[0, 20, 40, 60, float('inf')],
                labels=['simple', 'moderate', 'complex', 'very_complex']
            )
        
        # Priority indicator (combine multiple factors)
        if 'is_business_hours' in df.columns and 'duration_hours' in df.columns:
            df['business_impact_score'] = (
                df['is_business_hours'] * 0.4 +
                (df['duration_hours'] > 1).astype(int) * 0.3 +
                (1 - df.get('is_weekend', 0)) * 0.3
            )
        
        return df
    
    def _update_catalog(self, df: pd.DataFrame) -> None:
        """Update feature catalog with metadata."""
        self.feature_catalog = {
            'total_features': len(df.columns),
            'feature_names': list(df.columns),
            'temporal_features': [c for c in df.columns if 'hour' in c or 'day' in c or 'month' in c or 'week' in c],
            'runtime_features': [c for c in df.columns if 'duration' in c],
            'historical_features': [c for c in df.columns if 'failure' in c or 'success' in c or 'last' in c],
            'statistical_features': [c for c in df.columns if 'rolling' in c or 'zscore' in c or 'ema' in c],
            'business_features': [c for c in df.columns if 'business' in c or 'impact' in c or 'complexity' in c],
        }
    
    def get_feature_catalog(self) -> dict:
        """Get catalog of engineered features."""
        return self.feature_catalog
    
    def select_features(self, df: pd.DataFrame, feature_groups: List[str]) -> pd.DataFrame:
        """
        Select specific feature groups.
        
        Args:
            df: DataFrame with all features
            feature_groups: List of feature group names
            
        Returns:
            DataFrame with selected features only
        """
        selected_cols = []
        
        for group in feature_groups:
            group_key = f'{group}_features'
            if group_key in self.feature_catalog:
                selected_cols.extend(self.feature_catalog[group_key])
        
        # Add target and ID columns if present
        meta_cols = ['job_name', 'status', 'start_time', 'end_time']
        for col in meta_cols:
            if col in df.columns and col not in selected_cols:
                selected_cols.insert(0, col)
        
        return df[selected_cols]


# Singleton instance
_engineer = None

def get_feature_engineer() -> FeatureEngineer:
    """Get or create singleton feature engineer instance."""
    global _engineer
    if _engineer is None:
        _engineer = FeatureEngineer()
    return _engineer
