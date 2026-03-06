"""
Pattern Identification Agent
==============================

Discovers patterns and trends in job execution using:
- K-Means clustering
- DBSCAN for density-based patterns
- Time-series analysis
- Statistical pattern recognition

Identifies:
- Job groupings and dependencies
- Temporal execution patterns
- Resource usage patterns
- Performance trends
"""

from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from ..base_agent import BaseAgent
from ..config import PATTERN_IDENTIFICATION_CONFIG


class PatternIdentifierAgent(BaseAgent):
    """
    Agent for identifying patterns and trends in job execution.
    """
    
    def __init__(self):
        super().__init__('pattern_identifier')
        self.scaler = StandardScaler()
        self.pca = None
        self.kmeans_model = None
        self.dbscan_model = None
        self.feature_columns = []
        self.cluster_profiles = {}
        
    def train(self, data: pd.DataFrame) -> None:
        """
        Train pattern identification models on historical data.
        
        Args:
            data: Historical job execution data
        """
        self.logger.info(f"Training pattern identifier on {len(data)} records")
        
        # Preprocess and engineer features
        df = self.preprocess_data(data)
        df = self._engineer_features(df)
        
        # Prepare features
        X, feature_cols = self._prepare_features(df)
        self.feature_columns = feature_cols
        
        # Scale features
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        # Apply PCA for dimensionality reduction
        self.pca = PCA(n_components=min(10, X_scaled.shape[1]))
        X_pca = self.pca.fit_transform(X_scaled)
        
        # Train K-Means clustering
        kmeans_config = PATTERN_IDENTIFICATION_CONFIG['kmeans']
        self.kmeans_model = KMeans(
            n_clusters=kmeans_config['n_clusters'],
            random_state=kmeans_config['random_state'],
            max_iter=kmeans_config['max_iter'],
        )
        kmeans_labels = self.kmeans_model.fit_predict(X_pca)
        
        # Train DBSCAN for density-based clustering
        dbscan_config = PATTERN_IDENTIFICATION_CONFIG['dbscan']
        self.dbscan_model = DBSCAN(
            eps=dbscan_config['eps'],
            min_samples=dbscan_config['min_samples'],
        )
        dbscan_labels = self.dbscan_model.fit_predict(X_pca)
        
        # Analyze cluster profiles
        df['kmeans_cluster'] = kmeans_labels
        df['dbscan_cluster'] = dbscan_labels
        self.cluster_profiles = self._analyze_clusters(df)
        
        # Update status
        self.model = {
            'kmeans': self.kmeans_model,
            'dbscan': self.dbscan_model,
            'pca': self.pca,
        }
        self.is_trained = True
        self.last_trained = datetime.now()
        
        # Save model
        self.save_model()
        
        self.logger.info("Pattern identification training completed")
    
    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Assign patterns/clusters to new data.
        
        Args:
            data: New job execution data
            
        Returns:
            DataFrame with cluster assignments and pattern information
        """
        if not self.is_trained:
            self.logger.warning("Model not trained, loading from disk")
            if not self.load_model():
                raise RuntimeError("No trained model available")
            self.kmeans_model = self.model['kmeans']
            self.dbscan_model = self.model['dbscan']
            self.pca = self.model['pca']
        
        # Engineer features
        df = self.preprocess_data(data)
        df = self._engineer_features(df)
        
        # Prepare features
        X, _ = self._prepare_features(df)
        X_scaled = self.scaler.transform(X)
        X_pca = self.pca.transform(X_scaled)
        
        # Predict clusters
        kmeans_clusters = self.kmeans_model.predict(X_pca)
        dbscan_clusters = self.dbscan_model.fit_predict(X_pca)
        
        # Add to dataframe
        df['pattern_cluster'] = kmeans_clusters
        df['density_cluster'] = dbscan_clusters
        df['pattern_name'] = [self._get_pattern_name(c) for c in kmeans_clusters]
        df['is_outlier'] = (dbscan_clusters == -1).astype(int)
        
        return df
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze patterns and trends in data.
        
        Args:
            data: Job execution data
            
        Returns:
            Analysis with discovered patterns and trends
        """
        predictions = self.predict(data)
        
        # Pattern distribution
        pattern_dist = predictions['pattern_name'].value_counts().to_dict()
        
        # Outlier analysis
        outliers = predictions[predictions['is_outlier'] == 1]
        outlier_rate = len(outliers) / len(predictions) if len(predictions) > 0 else 0
        
        # Temporal patterns
        temporal_patterns = self._analyze_temporal_patterns(predictions)
        
        # Performance patterns
        performance_patterns = self._analyze_performance_patterns(predictions)
        
        # Trend analysis
        trends = self._analyze_trends(predictions)
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_jobs_analyzed': len(predictions),
            'pattern_distribution': pattern_dist,
            'cluster_profiles': self.cluster_profiles,
            'outliers_detected': len(outliers),
            'outlier_rate': round(outlier_rate, 4),
            'temporal_patterns': temporal_patterns,
            'performance_patterns': performance_patterns,
            'trends': trends,
            'recommendations': self._generate_recommendations(predictions, trends),
        }
        
        self.logger.info(f"Pattern analysis complete: {len(pattern_dist)} patterns identified")
        
        return analysis
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for pattern identification."""
        df = df.copy()
        
        # Temporal features
        if 'start_time' in df.columns:
            df = self.extract_temporal_features(df, 'start_time')
        
        # Runtime features
        if 'duration_seconds' in df.columns:
            df['duration_minutes'] = df['duration_seconds'] / 60
            df['duration_hours'] = df['duration_seconds'] / 3600
            
            # Categorize durations
            df['duration_category'] = pd.cut(
                df['duration_seconds'],
                bins=[0, 300, 1800, 3600, float('inf')],
                labels=['very_short', 'short', 'medium', 'long']
            )
        
        # Success patterns
        if 'status' in df.columns:
            df['is_success'] = (df['status'] == 'SUCCESS').astype(int)
        
        return df
    
    def _prepare_features(self, df: pd.DataFrame) -> tuple:
        """Prepare features for clustering."""
        feature_cols = [
            'duration_seconds',
            'hour_of_day',
            'day_of_week',
            'is_weekend',
            'is_business_hours',
        ]
        
        if 'is_success' in df.columns:
            feature_cols.append('is_success')
        
        # Filter to available columns
        available_cols = [col for col in feature_cols if col in df.columns]
        
        # Handle missing values
        df[available_cols] = df[available_cols].fillna(0)
        
        X = df[available_cols].values
        
        return X, available_cols
    
    def _analyze_clusters(self, df: pd.DataFrame) -> Dict[int, Dict[str, Any]]:
        """Analyze characteristics of each cluster."""
        profiles = {}
        
        for cluster_id in df['kmeans_cluster'].unique():
            cluster_data = df[df['kmeans_cluster'] == cluster_id]
            
            profile = {
                'size': len(cluster_data),
                'avg_duration': float(cluster_data['duration_seconds'].mean()) if 'duration_seconds' in cluster_data else 0,
                'peak_hour': int(cluster_data['hour_of_day'].mode().iloc[0]) if 'hour_of_day' in cluster_data and len(cluster_data['hour_of_day'].mode()) > 0 else 0,
                'success_rate': float(cluster_data['is_success'].mean()) if 'is_success' in cluster_data else 1.0,
                'weekend_pct': float(cluster_data['is_weekend'].mean()) if 'is_weekend' in cluster_data else 0.0,
            }
            
            profiles[int(cluster_id)] = profile
        
        return profiles
    
    def _get_pattern_name(self, cluster_id: int) -> str:
        """Get descriptive name for cluster pattern."""
        if cluster_id not in self.cluster_profiles:
            return f"Pattern_{cluster_id}"
        
        profile = self.cluster_profiles[cluster_id]
        
        # Generate descriptive name based on characteristics
        if profile['avg_duration'] < 600:  # < 10 minutes
            duration_desc = "Quick"
        elif profile['avg_duration'] < 3600:  # < 1 hour
            duration_desc = "Normal"
        else:
            duration_desc = "Long"
        
        if profile['peak_hour'] < 6 or profile['peak_hour'] > 22:
            time_desc = "Overnight"
        elif profile['peak_hour'] < 12:
            time_desc = "Morning"
        elif profile['peak_hour'] < 18:
            time_desc = "Afternoon"
        else:
            time_desc = "Evening"
        
        return f"{duration_desc}_{time_desc}_Jobs"
    
    def _analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze temporal execution patterns."""
        patterns = {}
        
        if 'hour_of_day' in df.columns:
            hourly_dist = df['hour_of_day'].value_counts().to_dict()
            peak_hours = sorted(hourly_dist.items(), key=lambda x: x[1], reverse=True)[:3]
            patterns['peak_hours'] = [{'hour': h, 'count': c} for h, c in peak_hours]
        
        if 'day_of_week' in df.columns:
            daily_dist = df['day_of_week'].value_counts().to_dict()
            patterns['daily_distribution'] = daily_dist
        
        if 'is_weekend' in df.columns:
            weekend_jobs = df[df['is_weekend'] == 1]
            patterns['weekend_execution_rate'] = len(weekend_jobs) / len(df) if len(df) > 0 else 0
        
        return patterns
    
    def _analyze_performance_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance-related patterns."""
        patterns = {}
        
        if 'duration_seconds' in df.columns:
            patterns['avg_duration'] = float(df['duration_seconds'].mean())
            patterns['median_duration'] = float(df['duration_seconds'].median())
            patterns['duration_std'] = float(df['duration_seconds'].std())
        
        if 'is_success' in df.columns:
            patterns['overall_success_rate'] = float(df['is_success'].mean())
            
            # Success rate by time of day
            if 'hour_of_day' in df.columns:
                hourly_success = df.groupby('hour_of_day')['is_success'].mean().to_dict()
                patterns['success_by_hour'] = hourly_success
        
        return patterns
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends over time."""
        trends = {}
        
        if 'start_time' in df.columns and len(df) > 10:
            df = df.sort_values('start_time')
            
            # Runtime trend
            if 'duration_seconds' in df.columns:
                recent_avg = df.tail(20)['duration_seconds'].mean()
                historical_avg = df['duration_seconds'].mean()
                runtime_change = ((recent_avg - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0
                trends['runtime_trend'] = {
                    'recent_avg': float(recent_avg),
                    'historical_avg': float(historical_avg),
                    'percent_change': round(float(runtime_change), 2),
                    'direction': 'increasing' if runtime_change > 5 else 'decreasing' if runtime_change < -5 else 'stable'
                }
            
            # Failure trend
            if 'is_success' in df.columns:
                recent_success = df.tail(20)['is_success'].mean()
                historical_success = df['is_success'].mean()
                success_change = recent_success - historical_success
                trends['success_trend'] = {
                    'recent_rate': round(float(recent_success), 4),
                    'historical_rate': round(float(historical_success), 4),
                    'change': round(float(success_change), 4),
                    'direction': 'improving' if success_change > 0.05 else 'degrading' if success_change < -0.05 else 'stable'
                }
        
        return trends
    
    def _generate_recommendations(self, df: pd.DataFrame, trends: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on patterns."""
        recommendations = []
        
        # Runtime trend recommendations
        if 'runtime_trend' in trends:
            rt_trend = trends['runtime_trend']
            if rt_trend['direction'] == 'increasing' and rt_trend['percent_change'] > 10:
                recommendations.append(
                    f"⚠️ Job runtimes increasing by {rt_trend['percent_change']:.1f}%. "
                    f"Review resource allocation and data volumes."
                )
        
        # Success trend recommendations
        if 'success_trend' in trends:
            st_trend = trends['success_trend']
            if st_trend['direction'] == 'degrading':
                recommendations.append(
                    f"⚠️ Success rate declining (now {st_trend['recent_rate']:.1%}). "
                    f"Investigate recent changes and error patterns."
                )
        
        # Outlier recommendations
        outliers = df[df['is_outlier'] == 1]
        if len(outliers) > len(df) * 0.1:
            recommendations.append(
                f"High number of outlier executions detected ({len(outliers)}). "
                f"Review unusual job behaviors."
            )
        
        # Pattern-based recommendations
        pattern_counts = df['pattern_name'].value_counts()
        if len(pattern_counts) > 0:
            dominant_pattern = pattern_counts.index[0]
            recommendations.append(
                f"Dominant execution pattern: {dominant_pattern} "
                f"({pattern_counts.iloc[0]} jobs, {pattern_counts.iloc[0]/len(df)*100:.1f}%)"
            )
        
        return recommendations
