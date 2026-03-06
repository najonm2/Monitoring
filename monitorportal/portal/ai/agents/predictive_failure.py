"""
Predictive Failure Analysis Agent
===================================

Predicts job failures before they occur using machine learning models.

Uses ensemble methods:
- Random Forest Classifier
- Gradient Boosting
- Feature importance analysis

Predicts:
- Probability of job failure
- Time to failure
- Root cause indicators
- Preventive actions
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from ..base_agent import BaseAgent
from ..config import PREDICTIVE_FAILURE_CONFIG


class PredictiveFailureAgent(BaseAgent):
    """
    Agent for predicting job failures using ensemble ML models.
    """
    
    def __init__(self):
        super().__init__('predictive_failure')
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.rf_model = None
        self.gb_model = None
        self.feature_importance = {}
        
    def train(self, data: pd.DataFrame) -> None:
        """
        Train failure prediction models on historical data.
        
        Args:
            data: Historical job execution data with outcomes
        """
        self.logger.info(f"Training predictive failure models on {len(data)} records")
        
        # Preprocess and engineer features
        df = self.preprocess_data(data)
        df = self._engineer_features(df)
        
        # Prepare features and target
        X, y, feature_cols = self._prepare_training_data(df)
        self.feature_columns = feature_cols
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        rf_config = PREDICTIVE_FAILURE_CONFIG['random_forest']
        self.rf_model = RandomForestClassifier(
            n_estimators=rf_config['n_estimators'],
            max_depth=rf_config['max_depth'],
            min_samples_split=rf_config['min_samples_split'],
            random_state=rf_config['random_state'],
            class_weight='balanced',
        )
        self.rf_model.fit(X_train_scaled, y_train)
        
        # Train Gradient Boosting
        gb_config = PREDICTIVE_FAILURE_CONFIG['gradient_boosting']
        self.gb_model = GradientBoostingClassifier(
            n_estimators=gb_config['n_estimators'],
            learning_rate=gb_config['learning_rate'],
            max_depth=gb_config['max_depth'],
            random_state=gb_config['random_state'],
        )
        self.gb_model.fit(X_train_scaled, y_train)
        
        # Evaluate models
        self._evaluate_models(X_test_scaled, y_test)
        
        # Calculate feature importance
        self._calculate_feature_importance()
        
        # Update status
        self.model = {'rf': self.rf_model, 'gb': self.gb_model}
        self.is_trained = True
        self.last_trained = datetime.now()
        
        # Save models
        self.save_model()
        
        self.logger.info("Predictive failure training completed")
    
    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Predict failure probability for jobs.
        
        Args:
            data: Current job data
            
        Returns:
            DataFrame with failure predictions and probabilities
        """
        if not self.is_trained:
            self.logger.warning("Model not trained, loading from disk")
            if not self.load_model():
                raise RuntimeError("No trained model available")
            self.rf_model = self.model['rf']
            self.gb_model = self.model['gb']
        
        # Engineer features
        df = self.preprocess_data(data)
        df = self._engineer_features(df)
        
        # Prepare features
        X = df[self.feature_columns].values
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from both models
        rf_proba = self.rf_model.predict_proba(X_scaled)[:, 1]
        gb_proba = self.gb_model.predict_proba(X_scaled)[:, 1]
        
        # Ensemble prediction (average)
        ensemble_proba = (rf_proba + gb_proba) / 2
        
        # Apply threshold
        threshold = PREDICTIVE_FAILURE_CONFIG['threshold']
        predictions = (ensemble_proba >= threshold).astype(int)
        
        # Add predictions to dataframe
        df['failure_probability'] = ensemble_proba
        df['predicted_failure'] = predictions
        df['risk_level'] = self._calculate_risk_level(ensemble_proba)
        df['confidence'] = self._calculate_confidence(rf_proba, gb_proba)
        
        return df
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze job data and generate failure predictions.
        
        Args:
            data: Job execution data
            
        Returns:
            Analysis with predictions and recommendations
        """
        predictions = self.predict(data)
        
        # Get high-risk jobs
        high_risk = predictions[predictions['risk_level'].isin(['HIGH', 'CRITICAL'])].copy()
        
        # Calculate statistics
        total_jobs = len(predictions)
        predicted_failures = len(predictions[predictions['predicted_failure'] == 1])
        failure_rate = predicted_failures / total_jobs if total_jobs > 0 else 0
        
        # Risk breakdown
        risk_counts = predictions['risk_level'].value_counts().to_dict()
        
        # Top at-risk jobs
        top_risk = self._get_top_risk_jobs(predictions, n=10)
        
        # Root cause analysis
        root_causes = self._analyze_root_causes(high_risk)
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_jobs_analyzed': total_jobs,
            'predicted_failures': predicted_failures,
            'predicted_failure_rate': round(failure_rate, 4),
            'risk_breakdown': risk_counts,
            'top_risk_jobs': top_risk,
            'root_causes': root_causes,
            'feature_importance': self.feature_importance,
            'recommendations': self._generate_recommendations(high_risk, root_causes),
        }
        
        self.logger.info(f"Analysis complete: {predicted_failures} potential failures predicted")
        
        return analysis
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer predictive features."""
        df = df.copy()
        
        # Temporal features
        if 'start_time' in df.columns:
            df = self.extract_temporal_features(df, 'start_time')
        
        # Historical failure features
        if 'job_name' in df.columns and 'status' in df.columns:
            df = self._add_historical_features(df)
        
        # Runtime features
        if 'duration_seconds' in df.columns:
            df = self.calculate_rolling_stats(df, 'duration_seconds', windows=[24, 168])
            df['duration_deviation'] = abs(
                df['duration_seconds'] - df['duration_seconds_rolling_mean_168h']
            ) / df['duration_seconds_rolling_std_168h']
        
        return df
    
    def _add_historical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add features based on historical job performance."""
        df = df.copy()
        df['is_failure'] = (df['status'] == 'FAILED').astype(int)
        
        # Failure counts in different time windows
        df = df.sort_values('start_time')
        df['failures_last_24h'] = df.groupby('job_name')['is_failure'].rolling(24, min_periods=1).sum().reset_index(0, drop=True)
        df['failures_last_7d'] = df.groupby('job_name')['is_failure'].rolling(168, min_periods=1).sum().reset_index(0, drop=True)
        
        # Success rate
        df['success_rate_24h'] = 1 - (df['failures_last_24h'] / 24)
        df['success_rate_7d'] = 1 - (df['failures_last_7d'] / 168)
        
        return df
    
    def _prepare_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare features and target for training."""
        # Define feature columns
        feature_cols = [
            'duration_seconds',
            'hour_of_day',
            'day_of_week',
            'is_weekend',
            'is_business_hours',
            'failures_last_24h',
            'success_rate_24h',
            'duration_deviation',
        ]
        
        # Filter to available columns
        available_cols = [col for col in feature_cols if col in df.columns]
        
        # Handle missing values
        df[available_cols] = df[available_cols].fillna(0)
        
        # Prepare X and y
        X = df[available_cols].values
        y = (df['status'] == 'FAILED').astype(int).values
        
        return X, y, available_cols
    
    def _evaluate_models(self, X_test: np.ndarray, y_test: np.ndarray) -> None:
        """Evaluate model performance on test set."""
        # Random Forest evaluation
        rf_pred = self.rf_model.predict(X_test)
        rf_proba = self.rf_model.predict_proba(X_test)[:, 1]
        rf_auc = roc_auc_score(y_test, rf_proba)
        
        # Gradient Boosting evaluation
        gb_pred = self.gb_model.predict(X_test)
        gb_proba = self.gb_model.predict_proba(X_test)[:, 1]
        gb_auc = roc_auc_score(y_test, gb_proba)
        
        self.logger.info(f"Random Forest ROC-AUC: {rf_auc:.4f}")
        self.logger.info(f"Gradient Boosting ROC-AUC: {gb_auc:.4f}")
    
    def _calculate_feature_importance(self) -> None:
        """Calculate and store feature importance."""
        rf_importance = self.rf_model.feature_importances_
        gb_importance = self.gb_model.feature_importances_
        
        # Average importance
        avg_importance = (rf_importance + gb_importance) / 2
        
        # Create dictionary
        self.feature_importance = {
            feature: float(importance)
            for feature, importance in zip(self.feature_columns, avg_importance)
        }
        
        # Sort by importance
        self.feature_importance = dict(
            sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)
        )
    
    def _calculate_risk_level(self, probabilities: np.ndarray) -> List[str]:
        """Calculate risk level based on failure probability."""
        thresholds = PREDICTIVE_FAILURE_CONFIG.get('alert_thresholds', {
            'critical': 0.8,
            'high': 0.6,
            'medium': 0.4,
            'low': 0.2,
        })
        
        risk_levels = []
        for prob in probabilities:
            if prob >= thresholds.get('critical', 0.8):
                risk_levels.append('CRITICAL')
            elif prob >= thresholds.get('high', 0.6):
                risk_levels.append('HIGH')
            elif prob >= thresholds.get('medium', 0.4):
                risk_levels.append('MEDIUM')
            elif prob >= thresholds.get('low', 0.2):
                risk_levels.append('LOW')
            else:
                risk_levels.append('MINIMAL')
        
        return risk_levels
    
    def _calculate_confidence(self, rf_proba: np.ndarray, gb_proba: np.ndarray) -> np.ndarray:
        """Calculate prediction confidence based on model agreement."""
        # Confidence is inversely related to disagreement
        disagreement = np.abs(rf_proba - gb_proba)
        confidence = 1 - disagreement
        return confidence
    
    def _get_top_risk_jobs(self, predictions: pd.DataFrame, n: int = 10) -> List[Dict]:
        """Get top N highest risk jobs."""
        top = predictions.nlargest(n, 'failure_probability')
        
        results = []
        for _, row in top.iterrows():
            results.append({
                'job_name': row.get('job_name', 'Unknown'),
                'failure_probability': round(float(row.get('failure_probability', 0)), 4),
                'risk_level': row.get('risk_level', 'UNKNOWN'),
                'confidence': round(float(row.get('confidence', 0)), 4),
                'recent_failures': int(row.get('failures_last_24h', 0)),
                'success_rate': round(float(row.get('success_rate_24h', 1)), 4),
            })
        
        return results
    
    def _analyze_root_causes(self, high_risk_jobs: pd.DataFrame) -> Dict[str, Any]:
        """Analyze potential root causes of predicted failures."""
        if len(high_risk_jobs) == 0:
            return {}
        
        root_causes = {
            'high_recent_failure_rate': 0,
            'runtime_anomalies': 0,
            'off_hours_execution': 0,
            'historical_patterns': 0,
        }
        
        for _, job in high_risk_jobs.iterrows():
            if job.get('failures_last_24h', 0) > 2:
                root_causes['high_recent_failure_rate'] += 1
            if abs(job.get('duration_deviation', 0)) > 2:
                root_causes['runtime_anomalies'] += 1
            if job.get('is_business_hours', 1) == 0:
                root_causes['off_hours_execution'] += 1
            if job.get('success_rate_7d', 1) < 0.8:
                root_causes['historical_patterns'] += 1
        
        return root_causes
    
    def _generate_recommendations(self, high_risk: pd.DataFrame, 
                                   root_causes: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if len(high_risk) == 0:
            recommendations.append("All jobs are predicted to run successfully.")
            return recommendations
        
        recommendations.append(
            f"⚠️ {len(high_risk)} jobs at HIGH or CRITICAL risk of failure."
        )
        
        if root_causes.get('high_recent_failure_rate', 0) > 0:
            recommendations.append(
                f"• {root_causes['high_recent_failure_rate']} jobs showing repeated failures. "
                f"Immediate investigation required."
            )
        
        if root_causes.get('runtime_anomalies', 0) > 0:
            recommendations.append(
                f"• {root_causes['runtime_anomalies']} jobs with unusual runtimes. "
                f"Check resource allocation and data volumes."
            )
        
        if root_causes.get('historical_patterns', 0) > 0:
            recommendations.append(
                f"• {root_causes['historical_patterns']} jobs with poor historical success rates. "
                f"Consider redesigning workflows or increasing monitoring."
            )
        
        return recommendations
