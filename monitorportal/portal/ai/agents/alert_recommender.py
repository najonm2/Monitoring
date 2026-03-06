"""
Alert and Recommendation Agent
================================

Generates intelligent alerts and actionable recommendations using:
- Priority scoring based on multiple factors
- Rule-based alerting system
- Recommendation engine
- Alert aggregation and deduplication

Provides:
- Prioritized alerts based on business impact
- Actionable recommendations
- Alert routing and escalation
- Historical context for decisions
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List
from collections import defaultdict

import numpy as np
import pandas as pd

from ..base_agent import BaseAgent
from ..config import ALERT_RECOMMENDER_CONFIG


class AlertRecommenderAgent(BaseAgent):
    """
    Agent for generating intelligent alerts and recommendations.
    """
    
    def __init__(self):
        super().__init__('alert_recommender')
        self.alert_history = []
        self.recommendation_cache = {}
        
    def train(self, data: pd.DataFrame) -> None:
        """
        Train on historical data to understand normal patterns.
        
        Args:
            data: Historical job data with outcomes
        """
        self.logger.info(f"Training alert recommender on {len(data)} records")
        
        # Analyze historical patterns for alert thresholds
        df = self.preprocess_data(data)
        
        # Calculate baseline metrics
        self.baseline_metrics = self._calculate_baselines(df)
        
        # Update status
        self.is_trained = True
        self.last_trained = datetime.now()
        self.model = {'baselines': self.baseline_metrics}
        
        # Save model
        self.save_model()
        
        self.logger.info("Alert recommender training completed")
    
    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate alert priorities for jobs.
        
        Args:
            data: Job data with predictions from other agents
            
        Returns:
            DataFrame with alert priorities and recommendations
        """
        df = data.copy()
        
        # Calculate priority scores
        df['priority_score'] = df.apply(self._calculate_priority, axis=1)
        df['alert_level'] = df['priority_score'].apply(self._map_to_alert_level)
        df['should_alert'] = (df['alert_level'].isin(['HIGH', 'CRITICAL'])).astype(int)
        
        return df
    
    def analyze(self, data: pd.DataFrame,
                anomaly_results: Dict[str, Any] = None,
                prediction_results: Dict[str, Any] = None,
                pattern_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate comprehensive alerts and recommendations.
        
        Args:
            data: Current job data
            anomaly_results: Results from anomaly detector
            prediction_results: Results from predictive failure agent
            pattern_results: Results from pattern identifier
            
        Returns:
            Consolidated alerts and recommendations
        """
        self.logger.info("Generating alerts and recommendations")
        
        # Get alert priorities
        df_with_alerts = self.predict(data)
        
        # Generate alerts
        alerts = self._generate_alerts(df_with_alerts, anomaly_results, 
                                        prediction_results, pattern_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            df_with_alerts, anomaly_results, prediction_results, pattern_results
        )
        
        # Deduplicate and prioritize
        alerts = self._deduplicate_alerts(alerts)
        recommendations = self._prioritize_recommendations(recommendations)
        
        # Create summary
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_alerts': len(alerts),
            'critical_alerts': len([a for a in alerts if a['level'] == 'CRITICAL']),
            'high_alerts': len([a for a in alerts if a['level'] == 'HIGH']),
            'alerts': alerts,
            'recommendations': recommendations,
            'summary': self._create_summary(alerts, recommendations),
        }
        
        # Store in history
        self.alert_history.append(analysis)
        
        self.logger.info(f"Generated {len(alerts)} alerts and {len(recommendations)} recommendations")
        
        return analysis
    
    def _calculate_baselines(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate baseline metrics from historical data."""
        baselines = {}
        
        if 'duration_seconds' in df.columns:
            baselines['avg_duration'] = float(df['duration_seconds'].mean())
            baselines['p95_duration'] = float(df['duration_seconds'].quantile(0.95))
        
        if 'status' in df.columns:
            baselines['failure_rate'] = float((df['status'] == 'FAILED').mean())
        
        return baselines
    
    def _calculate_priority(self, row: pd.Series) -> float:
        """Calculate priority score for a job."""
        weights = ALERT_RECOMMENDER_CONFIG['priority_weights']
        
        score = 0.0
        
        # Failure probability (from predictive agent)
        if 'failure_probability' in row:
            score += row['failure_probability'] * weights['failure_probability']
        
        # Runtime deviation (from anomaly detector)
        if 'duration_deviation' in row and pd.notna(row['duration_deviation']):
            deviation_score = min(abs(row['duration_deviation']) / 5, 1.0)
            score += deviation_score * weights['runtime_deviation']
        
        # Historical failures
        if 'failures_last_24h' in row:
            failure_score = min(row['failures_last_24h'] / 5, 1.0)
            score += failure_score * weights['historical_failures']
        
        # Business impact (simplified - can be enhanced with business rules)
        if 'is_business_hours' in row:
            business_impact = 1.0 if row['is_business_hours'] == 1 else 0.5
            score += business_impact * weights['business_impact']
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _map_to_alert_level(self, score: float) -> str:
        """Map priority score to alert level."""
        thresholds = ALERT_RECOMMENDER_CONFIG['alert_thresholds']
        
        if score >= thresholds['critical']:
            return 'CRITICAL'
        elif score >= thresholds['high']:
            return 'HIGH'
        elif score >= thresholds['medium']:
            return 'MEDIUM'
        elif score >= thresholds['low']:
            return 'LOW'
        else:
            return 'INFO'
    
    def _generate_alerts(self, df: pd.DataFrame,
                         anomaly_results: Dict[str, Any] = None,
                         prediction_results: Dict[str, Any] = None,
                         pattern_results: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate individual alerts."""
        alerts = []
        
        # Job-level alerts
        high_priority = df[df['alert_level'].isin(['HIGH', 'CRITICAL'])]
        for _, job in high_priority.iterrows():
            alert = {
                'id': f"JOB_{job.get('job_name', 'unknown')}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'level': job['alert_level'],
                'type': 'job_alert',
                'job_name': job.get('job_name', 'Unknown'),
                'priority_score': round(float(job['priority_score']), 4),
                'message': self._create_alert_message(job),
                'timestamp': datetime.now().isoformat(),
                'details': self._extract_alert_details(job),
            }
            alerts.append(alert)
        
        # System-level alerts from anomaly detector
        if anomaly_results and anomaly_results.get('anomaly_rate', 0) > 0.15:
            alerts.append({
                'id': f"SYS_ANOMALY_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'level': 'HIGH',
                'type': 'system_alert',
                'message': f"High anomaly rate detected: {anomaly_results['anomaly_rate']:.1%}",
                'timestamp': datetime.now().isoformat(),
                'details': anomaly_results,
            })
        
        # Failure prediction alerts
        if prediction_results and prediction_results.get('predicted_failure_rate', 0) > 0.2:
            alerts.append({
                'id': f"SYS_FAILURE_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'level': 'CRITICAL',
                'type': 'prediction_alert',
                'message': f"High failure rate predicted: {prediction_results['predicted_failure_rate']:.1%}",
                'timestamp': datetime.now().isoformat(),
                'details': prediction_results,
            })
        
        # Pattern deviation alerts
        if pattern_results:
            trends = pattern_results.get('trends', {})
            if 'runtime_trend' in trends and trends['runtime_trend'].get('direction') == 'increasing':
                pct_change = trends['runtime_trend'].get('percent_change', 0)
                if pct_change > 20:
                    alerts.append({
                        'id': f"SYS_PERFORMANCE_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        'level': 'HIGH',
                        'type': 'performance_alert',
                        'message': f"Significant runtime increase detected: {pct_change:.1f}%",
                        'timestamp': datetime.now().isoformat(),
                        'details': trends['runtime_trend'],
                    })
        
        return alerts
    
    def _create_alert_message(self, job: pd.Series) -> str:
        """Create human-readable alert message."""
        job_name = job.get('job_name', 'Unknown Job')
        
        reasons = []
        
        if 'failure_probability' in job and job['failure_probability'] > 0.7:
            reasons.append(f"high failure risk ({job['failure_probability']:.1%})")
        
        if 'anomaly_score' in job and job.get('is_anomaly', 0) == 1:
            reasons.append("anomalous behavior detected")
        
        if 'failures_last_24h' in job and job['failures_last_24h'] > 2:
            reasons.append(f"{int(job['failures_last_24h'])} recent failures")
        
        reason_text = ", ".join(reasons) if reasons else "multiple risk factors"
        
        return f"⚠️ {job_name}: {reason_text}"
    
    def _extract_alert_details(self, job: pd.Series) -> Dict[str, Any]:
        """Extract relevant details for alert."""
        details = {
            'job_name': job.get('job_name', 'Unknown'),
        }
        
        detail_fields = [
            'failure_probability', 'anomaly_score', 'priority_score',
            'duration_seconds', 'failures_last_24h', 'success_rate_24h',
            'risk_level', 'pattern_name'
        ]
        
        for field in detail_fields:
            if field in job and pd.notna(job[field]):
                value = job[field]
                if isinstance(value, (np.integer, np.floating)):
                    value = float(value)
                details[field] = value
        
        return details
    
    def _generate_recommendations(self, df: pd.DataFrame,
                                   anomaly_results: Dict[str, Any] = None,
                                   prediction_results: Dict[str, Any] = None,
                                   pattern_results: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Job-specific recommendations
        high_risk_jobs = df[df.get('failure_probability', pd.Series(0)) > 0.7]
        if len(high_risk_jobs) > 0:
            for _, job in high_risk_jobs.head(5).iterrows():
                recommendations.append({
                    'type': 'immediate_action',
                    'priority': 'HIGH',
                    'target': job.get('job_name', 'Unknown'),
                    'recommendation': f"Review and potentially disable job due to {job.get('failure_probability', 0):.0%} failure probability",
                    'actions': [
                        'Check recent error logs',
                        'Verify data sources are available',
                        'Review resource allocation',
                        'Consider manual execution with monitoring'
                    ]
                })
        
        # Aggregate recommendations from other agents
        if anomaly_results and 'recommendations' in anomaly_results:
            for rec in anomaly_results['recommendations']:
                recommendations.append({
                    'type': 'anomaly',
                    'priority': 'MEDIUM',
                    'recommendation': rec,
                })
        
        if prediction_results and 'recommendations' in prediction_results:
            for rec in prediction_results['recommendations']:
                recommendations.append({
                    'type': 'predictive',
                    'priority': 'MEDIUM',
                    'recommendation': rec,
                })
        
        if pattern_results and 'recommendations' in pattern_results:
            for rec in pattern_results['recommendations']:
                recommendations.append({
                    'type': 'pattern',
                    'priority': 'LOW',
                    'recommendation': rec,
                })
        
        # System-level recommendations
        if len(df) > 0:
            overall_failure_rate = df.get('failure_probability', pd.Series(0)).mean()
            if overall_failure_rate > 0.3:
                recommendations.append({
                    'type': 'system_health',
                    'priority': 'HIGH',
                    'recommendation': f"System-wide failure risk is elevated ({overall_failure_rate:.1%})",
                    'actions': [
                        'Review recent infrastructure changes',
                        'Check system resource availability',
                        'Verify database connectivity',
                        'Consider throttling job execution'
                    ]
                })
        
        return recommendations
    
    def _deduplicate_alerts(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate alerts."""
        seen = set()
        unique_alerts = []
        
        for alert in alerts:
            # Create signature based on type and target
            signature = (
                alert.get('type'),
                alert.get('job_name', alert.get('message', ''))[:50]
            )
            
            if signature not in seen:
                seen.add(signature)
                unique_alerts.append(alert)
        
        return unique_alerts
    
    def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort recommendations by priority."""
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        
        return sorted(
            recommendations,
            key=lambda x: priority_order.get(x.get('priority', 'LOW'), 3)
        )
    
    def _create_summary(self, alerts: List[Dict[str, Any]],
                        recommendations: List[Dict[str, Any]]) -> str:
        """Create executive summary."""
        critical_count = len([a for a in alerts if a.get('level') == 'CRITICAL'])
        high_count = len([a for a in alerts if a.get('level') == 'HIGH'])
        
        if critical_count > 0:
            return (
                f"🚨 CRITICAL: {critical_count} critical alerts require immediate attention. "
                f"{len(recommendations)} recommendations available."
            )
        elif high_count > 0:
            return (
                f"⚠️ WARNING: {high_count} high-priority alerts detected. "
                f"Review recommendations and take action."
            )
        else:
            return "✅ System operating normally. No critical issues detected."
