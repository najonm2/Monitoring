"""
AI Orchestrator
================

Coordinates all AI agents and manages the overall AI workflow.

Responsibilities:
- Initialize and manage all agents
- Fetch data from Oracle databases
- Coordinate agent execution
- Aggregate results from all agents
- Manage model training and retraining
- Cache results for performance
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import pandas as pd

from .agents.anomaly_detector import AnomalyDetectorAgent
from .agents.predictive_failure import PredictiveFailureAgent
from .agents.pattern_identifier import PatternIdentifierAgent
from .agents.alert_recommender import AlertRecommenderAgent
from .config import EXECUTION_CONFIG, LOGGING_CONFIG


class AIOrchestrator:
    """
    Main orchestrator for the AI agent system.
    Coordinates all agents and manages data flow.
    """
    
    def __init__(self):
        """Initialize the orchestrator and all agents."""
        self.logger = self._setup_logger()
        
        # Initialize agents
        self.logger.info("Initializing AI agents...")
        self.anomaly_detector = AnomalyDetectorAgent()
        self.predictive_failure = PredictiveFailureAgent()
        self.pattern_identifier = PatternIdentifierAgent()
        self.alert_recommender = AlertRecommenderAgent()
        
        # Agent registry
        self.agents = {
            'anomaly_detector': self.anomaly_detector,
            'predictive_failure': self.predictive_failure,
            'pattern_identifier': self.pattern_identifier,
            'alert_recommender': self.alert_recommender,
        }
        
        # Result cache
        self.cache = {}
        self.cache_timeout = timedelta(minutes=EXECUTION_CONFIG['update_frequency_minutes'])
        self.last_execution = None
        
        self.logger.info("AI Orchestrator initialized successfully")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for orchestrator."""
        logger = logging.getLogger('ai_orchestrator')
        logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))
        
        fh = logging.FileHandler(LOGGING_CONFIG['file'])
        fh.setLevel(logging.DEBUG)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter(LOGGING_CONFIG['format'])
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def train_all_agents(self, training_data: pd.DataFrame) -> Dict[str, bool]:
        """
        Train all agents on historical data.
        
        Args:
            training_data: Historical job execution data
            
        Returns:
            Dictionary with training status for each agent
        """
        self.logger.info(f"Training all agents with {len(training_data)} records")
        
        results = {}
        
        for agent_name, agent in self.agents.items():
            try:
                self.logger.info(f"Training {agent_name}...")
                agent.train(training_data)
                results[agent_name] = True
                self.logger.info(f"{agent_name} trained successfully")
            except Exception as e:
                self.logger.error(f"Failed to train {agent_name}: {str(e)}")
                results[agent_name] = False
        
        return results
    
    def load_all_agents(self) -> Dict[str, bool]:
        """
        Load all pre-trained agents from disk.
        
        Returns:
            Dictionary with load status for each agent
        """
        self.logger.info("Loading all agents from disk")
        
        results = {}
        
        for agent_name, agent in self.agents.items():
            try:
                success = agent.load_model()
                results[agent_name] = success
                if success:
                    self.logger.info(f"{agent_name} loaded successfully")
                else:
                    self.logger.warning(f"No saved model for {agent_name}")
            except Exception as e:
                self.logger.error(f"Failed to load {agent_name}: {str(e)}")
                results[agent_name] = False
        
        return results
    
    def check_retraining_needed(self) -> Dict[str, bool]:
        """
        Check which agents need retraining.
        
        Returns:
            Dictionary indicating which agents need retraining
        """
        retrain_days = EXECUTION_CONFIG['model_retrain_days']
        
        results = {}
        for agent_name, agent in self.agents.items():
            needs_retrain = agent.needs_retraining(retrain_days)
            results[agent_name] = needs_retrain
        
        return results
    
    def run_analysis(self, current_data: pd.DataFrame,
                     force_refresh: bool = False) -> Dict[str, Any]:
        """
        Run complete AI analysis on current job data.
        
        Args:
            current_data: Current job execution data
            force_refresh: Force fresh analysis ignoring cache
            
        Returns:
            Comprehensive analysis results from all agents
        """
        # Check cache
        if not force_refresh and self._is_cache_valid():
            self.logger.info("Returning cached results")
            return self.cache.get('results', {})
        
        self.logger.info(f"Running AI analysis on {len(current_data)} jobs")
        
        try:
            # Ensure agents are loaded
            self._ensure_agents_loaded()
            
            # Run each agent
            results = {}
            
            # 1. Anomaly Detection
            self.logger.info("Running anomaly detection...")
            anomaly_results = self.anomaly_detector.analyze(current_data)
            results['anomaly_detection'] = anomaly_results
            
            # 2. Predictive Failure Analysis
            self.logger.info("Running predictive failure analysis...")
            prediction_results = self.predictive_failure.analyze(current_data)
            results['predictive_failure'] = prediction_results
            
            # 3. Pattern Identification
            self.logger.info("Running pattern identification...")
            pattern_results = self.pattern_identifier.analyze(current_data)
            results['pattern_identification'] = pattern_results
            
            # 4. Alert & Recommendations (uses results from other agents)
            self.logger.info("Generating alerts and recommendations...")
            alert_results = self.alert_recommender.analyze(
                current_data,
                anomaly_results=anomaly_results,
                prediction_results=prediction_results,
                pattern_results=pattern_results
            )
            results['alerts_recommendations'] = alert_results
            
            # Create executive summary
            results['summary'] = self._create_executive_summary(results)
            results['timestamp'] = datetime.now().isoformat()
            results['jobs_analyzed'] = len(current_data)
            
            # Cache results
            self.cache['results'] = results
            self.cache['timestamp'] = datetime.now()
            self.last_execution = datetime.now()
            
            self.logger.info("AI analysis completed successfully")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error during analysis: {str(e)}")
            raise
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all agents.
        
        Returns:
            Status information for all agents
        """
        status = {
            'orchestrator_status': 'operational',
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'cache_valid': self._is_cache_valid(),
            'agents': {}
        }
        
        for agent_name, agent in self.agents.items():
            status['agents'][agent_name] = agent.get_status()
        
        return status
    
    def get_insights_summary(self) -> Dict[str, Any]:
        """
        Get high-level summary of latest insights.
        
        Returns:
            Summary of key insights from all agents
        """
        if not self.cache.get('results'):
            return {
                'status': 'no_analysis_available',
                'message': 'No analysis has been run yet'
            }
        
        results = self.cache['results']
        
        summary = {
            'timestamp': results.get('timestamp'),
            'jobs_analyzed': results.get('jobs_analyzed', 0),
            'anomalies': {
                'count': results.get('anomaly_detection', {}).get('anomalies_detected', 0),
                'rate': results.get('anomaly_detection', {}).get('anomaly_rate', 0),
            },
            'predictions': {
                'predicted_failures': results.get('predictive_failure', {}).get('predicted_failures', 0),
                'failure_rate': results.get('predictive_failure', {}).get('predicted_failure_rate', 0),
            },
            'patterns': {
                'patterns_identified': len(results.get('pattern_identification', {}).get('pattern_distribution', {})),
                'outliers': results.get('pattern_identification', {}).get('outliers_detected', 0),
            },
            'alerts': {
                'total': results.get('alerts_recommendations', {}).get('total_alerts', 0),
                'critical': results.get('alerts_recommendations', {}).get('critical_alerts', 0),
                'high': results.get('alerts_recommendations', {}).get('high_alerts', 0),
            },
            'executive_summary': results.get('summary', {}).get('executive_summary', ''),
        }
        
        return summary
    
    def _ensure_agents_loaded(self) -> None:
        """Ensure all agents have models loaded."""
        for agent_name, agent in self.agents.items():
            if not agent.is_trained:
                self.logger.warning(f"{agent_name} not trained, attempting to load...")
                if not agent.load_model():
                    raise RuntimeError(
                        f"{agent_name} has no trained model. "
                        f"Please train the agent first using train_all_agents()."
                    )
    
    def _is_cache_valid(self) -> bool:
        """Check if cached results are still valid."""
        if 'timestamp' not in self.cache:
            return False
        
        cache_age = datetime.now() - self.cache['timestamp']
        return cache_age < self.cache_timeout
    
    def _create_executive_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary from all agent results."""
        # Extract key metrics
        anomalies = results.get('anomaly_detection', {}).get('anomalies_detected', 0)
        predicted_failures = results.get('predictive_failure', {}).get('predicted_failures', 0)
        critical_alerts = results.get('alerts_recommendations', {}).get('critical_alerts', 0)
        high_alerts = results.get('alerts_recommendations', {}).get('high_alerts', 0)
        
        # Determine overall health
        if critical_alerts > 0:
            health_status = 'CRITICAL'
            health_color = 'red'
        elif high_alerts > 5 or predicted_failures > 10:
            health_status = 'WARNING'
            health_color = 'orange'
        elif anomalies > 5:
            health_status = 'ATTENTION'
            health_color = 'yellow'
        else:
            health_status = 'HEALTHY'
            health_color = 'green'
        
        # Create summary text
        if health_status == 'CRITICAL':
            summary_text = (
                f"🚨 CRITICAL: System requires immediate attention. "
                f"{critical_alerts} critical alerts detected."
            )
        elif health_status == 'WARNING':
            summary_text = (
                f"⚠️ WARNING: Elevated risk levels detected. "
                f"{predicted_failures} jobs at risk of failure."
            )
        elif health_status == 'ATTENTION':
            summary_text = (
                f"ℹ️ ATTENTION: Some anomalies detected. "
                f"{anomalies} jobs showing unusual patterns."
            )
        else:
            summary_text = "✅ HEALTHY: System operating normally."
        
        # Top recommendations
        alert_recs = results.get('alerts_recommendations', {}).get('recommendations', [])
        top_recommendations = alert_recs[:3] if alert_recs else []
        
        summary = {
            'health_status': health_status,
            'health_color': health_color,
            'executive_summary': summary_text,
            'key_metrics': {
                'anomalies_detected': anomalies,
                'predicted_failures': predicted_failures,
                'critical_alerts': critical_alerts,
                'high_alerts': high_alerts,
            },
            'top_recommendations': top_recommendations,
            'requires_action': health_status in ['CRITICAL', 'WARNING'],
        }
        
        return summary
    
    def fetch_and_analyze(self, application: str = 'all') -> Dict[str, Any]:
        """
        Fetch data from Oracle and run analysis.
        
        Args:
            application: 'level3', 'mdm', 'erp', or 'all'
            
        Returns:
            Complete analysis results
        """
        self.logger.info(f"Fetching data for application: {application}")
        
        try:
            # Import here to avoid circular dependency
            from ..services.level3_service import (
                get_level3_failed_with_error,
                get_level3_long_running,
                get_mdm_job_status,
                get_erp_job_status
            )
            
            # Fetch data based on application
            data_frames = []
            
            if application in ['level3', 'all']:
                level3_failed = get_level3_failed_with_error()
                level3_long = get_level3_long_running()
                if level3_failed:
                    data_frames.append(pd.DataFrame(level3_failed))
                if level3_long:
                    data_frames.append(pd.DataFrame(level3_long))
            
            if application in ['mdm', 'all']:
                mdm_data = get_mdm_job_status()
                if mdm_data:
                    data_frames.append(pd.DataFrame(mdm_data))
            
            if application in ['erp', 'all']:
                erp_data = get_erp_job_status()
                if erp_data:
                    data_frames.append(pd.DataFrame(erp_data))
            
            # Combine data
            if not data_frames:
                raise ValueError("No data available from any source")
            
            combined_data = pd.concat(data_frames, ignore_index=True)
            
            # Run analysis
            results = self.run_analysis(combined_data)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error fetching and analyzing data: {str(e)}")
            raise


# Singleton instance
_orchestrator = None

def get_orchestrator() -> AIOrchestrator:
    """Get or create the singleton orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AIOrchestrator()
    return _orchestrator
