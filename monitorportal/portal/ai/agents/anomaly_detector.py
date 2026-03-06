"""
Anomaly Detection Agent
========================

Detects unusual patterns and anomalies in job execution using:
- Isolation Forest for outlier detection
- Statistical thresholds
- Time-series analysis

Identifies:
- Unusual runtime durations
- Unexpected failure patterns
- Abnormal resource usage
- Irregular scheduling patterns
"""

from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from ..base_agent import BaseAgent
from ..config import ANOMALY_DETECTION_CONFIG


class AnomalyDetectorAgent(BaseAgent):
    """
    Agent for detecting anomalies in job execution patterns.
    """
    
    def __init__(self):
        super().__init__('anomaly_detector')
        self.scaler = StandardScaler()
        self.feature_columns = []
        
    def train(self, data: pd.DataFrame) -> None:
        """
        Train anomaly detection model on historical data.
        
        Args:
            data: Historical job execution data with columns:
                - duration_seconds: Job runtime
                - start_time: Job start timestamp
                - status: Job outcome (SUCCESS/FAILED)
                - job_name: Job identifier
        """
        self.logger.info(f"Training anomaly detector on {len(data)} records")
        
        # Preprocess and engineer features
        df = self.preprocess_data(data)
        df = self._engineer_features(df)
        
        # Select feature columns
        self.feature_columns = [
            'duration_seconds',
            'hour_of_day',
            'day_of_week',
            'is_weekend',
            'duration_z_score',
            'failure_rate_24h',
        ]
        
        # Prepare features
        X = df[self.feature_columns].values
        
        # Train scaler
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        # Train Isolation Forest
        config = ANOMALY_DETECTION_CONFIG['isolation_forest']
        self.model = IsolationForest(
            contamination=config['contamination'],
            n_estimators=config['n_estimators'],
            max_samples=config['max_samples'],
            random_state=config['random_state'],
        )
        
        self.model.fit(X_scaled)
        
        # Update training status
        self.is_trained = True
        self.last_trained = datetime.now()
        
        # Save model
        self.save_model()
        
        self.logger.info("Anomaly detector training completed")
    
    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Predict anomalies in new data.
        
        Args:
            data: New job execution data
            
        Returns:
            DataFrame with anomaly predictions and scores
        """
        if not self.is_trained:
            self.logger.warning("Model not trained, loading from disk")
            if not self.load_model():
                raise RuntimeError("No trained model available")
        
        # Engineer features
        df = self.preprocess_data(data)
        df = self._engineer_features(df)
        
        # Prepare features
        X = df[self.feature_columns].values
        X_scaled = self.scaler.transform(X)
        
        # Predict anomalies
        predictions = self.model.predict(X_scaled)  # -1 for anomalies, 1 for normal
        scores = self.model.score_samples(X_scaled)  # Anomaly scores (lower = more anomalous)
        
        # Add predictions to dataframe
        df['is_anomaly'] = (predictions == -1).astype(int)
        df['anomaly_score'] = scores
        df['anomaly_severity'] = self._calculate_severity(scores)
        
        return df
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze data and generate anomaly insights.
        
        Args:
            data: Job execution data
            
        Returns:
            Analysis results with detected anomalies and patterns
        """
        predictions = self.predict(data)
        
        # Get anomalies
        anomalies = predictions[predictions['is_anomaly'] == 1].copy()
        
        # Categorize anomalies
        anomaly_types = self._categorize_anomalies(anomalies)
        
        # Calculate statistics
        total_jobs = len(predictions)
        anomaly_count = len(anomalies)
        anomaly_rate = anomaly_count / total_jobs if total_jobs > 0 else 0
        
        # Severity breakdown
        severity_counts = anomalies['anomaly_severity'].value_counts().to_dict()
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_jobs_analyzed': total_jobs,
            'anomalies_detected': anomaly_count,
            'anomaly_rate': round(anomaly_rate, 4),
            'severity_breakdown': severity_counts,
            'anomaly_types': anomaly_types,
            'top_anomalies': self._get_top_anomalies(anomalies, n=10),
            'recommendations': self._generate_recommendations(anomalies),
        }
        
        self.logger.info(f"Analysis complete: {anomaly_count} anomalies detected")
        
        return analysis
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for anomaly detection."""
        df = df.copy()
        
        # Temporal features
        if 'start_time' in df.columns:
            df = self.extract_temporal_features(df, 'start_time')
        
        # Duration statistics
        if 'duration_seconds' in df.columns:
            mean_duration = df['duration_seconds'].mean()
            std_duration = df['duration_seconds'].std()
            df['duration_z_score'] = (df['duration_seconds'] - mean_duration) / std_duration
        
        # Failure rate features
        if 'status' in df.columns:
            df['is_failure'] = (df['status'] == 'FAILED').astype(int)
            df['failure_rate_24h'] = df['is_failure'].rolling(window=24, min_periods=1).mean()
        
        return df
    
    def _calculate_severity(self, scores: np.ndarray) -> List[str]:
        """
        Calculate severity level based on anomaly scores.
        
        Args:
            scores: Anomaly scores from model
            
        Returns:
            List of severity levels
        """
        # Lower scores indicate more severe anomalies
        percentiles = np.percentile(scores, [25, 50, 75])
        
        severity = []
        for score in scores:
            if score < percentiles[0]:
                severity.append('CRITICAL')
            elif score < percentiles[1]:
                severity.append('HIGH')
            elif score < percentiles[2]:
                severity.append('MEDIUM')
            else:
                severity.append('LOW')
        
        return severity
    
    def _categorize_anomalies(self, anomalies: pd.DataFrame) -> Dict[str, int]:
        """Categorize anomalies by type."""
        categories = {
            'runtime_anomaly': 0,
            'timing_anomaly': 0,
            'failure_anomaly': 0,
            'general_anomaly': 0,
        }
        
        for _, row in anomalies.iterrows():
            if 'duration_z_score' in row and abs(row['duration_z_score']) > 3:
                categories['runtime_anomaly'] += 1
            elif 'is_business_hours' in row and row['is_business_hours'] == 0:
                categories['timing_anomaly'] += 1
            elif 'is_failure' in row and row['is_failure'] == 1:
                categories['failure_anomaly'] += 1
            else:
                categories['general_anomaly'] += 1
        
        return categories
    
    def _get_top_anomalies(self, anomalies: pd.DataFrame, n: int = 10) -> List[Dict]:
        """Get top N most severe anomalies."""
        if len(anomalies) == 0:
            return []
        
        top = anomalies.nsmallest(n, 'anomaly_score')
        
        results = []
        for _, row in top.iterrows():
            results.append({
                'job_name': row.get('job_name', 'Unknown'),
                'start_time': row.get('start_time', '').isoformat() if hasattr(row.get('start_time', ''), 'isoformat') else str(row.get('start_time', '')),
                'duration_seconds': int(row.get('duration_seconds', 0)),
                'status': row.get('status', 'Unknown'),
                'anomaly_score': float(row.get('anomaly_score', 0)),
                'severity': row.get('anomaly_severity', 'UNKNOWN'),
            })
        
        return results
    
    def _generate_recommendations(self, anomalies: pd.DataFrame) -> List[str]:
        """Generate recommendations based on detected anomalies."""
        recommendations = []
        
        if len(anomalies) == 0:
            recommendations.append("No anomalies detected. System is operating normally.")
            return recommendations
        
        # Runtime anomalies
        runtime_anomalies = anomalies[anomalies.get('duration_z_score', pd.Series()).abs() > 3]
        if len(runtime_anomalies) > 0:
            recommendations.append(
                f"Found {len(runtime_anomalies)} jobs with unusual runtimes. "
                f"Review job configurations and resource allocation."
            )
        
        # Off-hours execution
        off_hours = anomalies[anomalies.get('is_business_hours', pd.Series()) == 0]
        if len(off_hours) > 5:
            recommendations.append(
                f"Detected {len(off_hours)} jobs running outside business hours. "
                f"Verify scheduling configuration."
            )
        
        # High severity anomalies
        critical = anomalies[anomalies['anomaly_severity'] == 'CRITICAL']
        if len(critical) > 0:
            recommendations.append(
                f"⚠️ {len(critical)} CRITICAL anomalies require immediate attention."
            )
        
        return recommendations
