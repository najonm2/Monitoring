"""
Model Training Module
======================

Utilities for training and managing AI models.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

from .orchestrator import get_orchestrator
from .feature_engineering import get_feature_engineer
from ..services.level3_service import (
    get_level3_failed_with_error,
    get_level3_long_running,
    get_mdm_job_status,
    get_erp_job_status,
)


logger = logging.getLogger(__name__)


def fetch_training_data(lookback_days: int = 90, applications: List[str] = None) -> pd.DataFrame:
    """
    Fetch historical data for training.
    
    Args:
        lookback_days: Number of days of history to fetch
        applications: List of applications to include (None = all)
        
    Returns:
        Combined DataFrame with training data
    """
    logger.info(f"Fetching training data for last {lookback_days} days")
    
    data_frames = []
    apps_to_fetch = applications or ['level3', 'mdm', 'erp']
    
    try:
        if 'level3' in apps_to_fetch:
            level3_failed = get_level3_failed_with_error()
            level3_long = get_level3_long_running()
            
            if level3_failed:
                df_failed = pd.DataFrame(level3_failed)
                df_failed['source'] = 'level3_failed'
                data_frames.append(df_failed)
            
            if level3_long:
                df_long = pd.DataFrame(level3_long)
                df_long['source'] = 'level3_long'
                data_frames.append(df_long)
        
        if 'mdm' in apps_to_fetch:
            mdm_data = get_mdm_job_status()
            if mdm_data:
                df_mdm = pd.DataFrame(mdm_data)
                df_mdm['source'] = 'mdm'
                data_frames.append(df_mdm)
        
        if 'erp' in apps_to_fetch:
            erp_data = get_erp_job_status()
            if erp_data:
                df_erp = pd.DataFrame(erp_data)
                df_erp['source'] = 'erp'
                data_frames.append(df_erp)
        
        if not data_frames:
            raise ValueError("No training data available from any source")
        
        # Combine all data
        combined = pd.concat(data_frames, ignore_index=True)
        
        logger.info(f"Fetched {len(combined)} records from {len(data_frames)} sources")
        
        return combined
        
    except Exception as e:
        logger.error(f"Error fetching training data: {str(e)}")
        raise


def prepare_training_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare raw data for training with feature engineering.
    
    Args:
        raw_data: Raw job execution data
        
    Returns:
        Processed data with engineered features
    """
    logger.info("Preparing training data with feature engineering")
    
    # Get feature engineer
    engineer = get_feature_engineer()
    
    # Apply feature engineering
    processed_data = engineer.transform(raw_data)
    
    logger.info(f"Generated {len(processed_data.columns)} features")
    
    return processed_data


def train_all_models(training_data: Optional[pd.DataFrame] = None,
                     lookback_days: int = 90) -> Dict[str, bool]:
    """
    Train all AI models.
    
    Args:
        training_data: Pre-fetched training data (optional)
        lookback_days: Days of history if fetching data
        
    Returns:
        Training status for each model
    """
    logger.info("Starting training for all AI models")
    
    try:
        # Fetch data if not provided
        if training_data is None:
            training_data = fetch_training_data(lookback_days)
        
        # Prepare data
        prepared_data = prepare_training_data(training_data)
        
        # Get orchestrator
        orchestrator = get_orchestrator()
        
        # Train all agents
        results = orchestrator.train_all_agents(prepared_data)
        
        # Log results
        for agent_name, success in results.items():
            if success:
                logger.info(f"✓ {agent_name} trained successfully")
            else:
                logger.error(f"✗ {agent_name} training failed")
        
        return results
        
    except Exception as e:
        logger.error(f"Error during model training: {str(e)}")
        raise


def load_all_models() -> Dict[str, bool]:
    """
    Load all pre-trained models from disk.
    
    Returns:
        Load status for each model
    """
    logger.info("Loading all AI models from disk")
    
    try:
        orchestrator = get_orchestrator()
        results = orchestrator.load_all_agents()
        
        # Log results
        for agent_name, success in results.items():
            if success:
                logger.info(f"✓ {agent_name} loaded successfully")
            else:
                logger.warning(f"⚠ {agent_name} not loaded (no saved model)")
        
        return results
        
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise


def check_model_health() -> Dict[str, any]:
    """
    Check health status of all models.
    
    Returns:
        Health status information
    """
    logger.info("Checking model health")
    
    try:
        orchestrator = get_orchestrator()
        
        # Get agent status
        status = orchestrator.get_agent_status()
        
        # Check retraining needs
        retraining_needed = orchestrator.check_retraining_needed()
        
        # Compile health report
        health = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'agents': {},
            'warnings': [],
        }
        
        for agent_name, agent_status in status['agents'].items():
            agent_health = {
                'is_trained': agent_status['is_trained'],
                'last_trained': agent_status['last_trained'],
                'needs_retraining': retraining_needed.get(agent_name, False),
                'model_exists': agent_status['model_exists'],
            }
            
            # Determine agent status
            if not agent_health['is_trained']:
                agent_health['status'] = 'not_trained'
                health['warnings'].append(f"{agent_name} is not trained")
                health['overall_status'] = 'degraded'
            elif agent_health['needs_retraining']:
                agent_health['status'] = 'needs_retraining'
                health['warnings'].append(f"{agent_name} needs retraining")
            else:
                agent_health['status'] = 'healthy'
            
            health['agents'][agent_name] = agent_health
        
        return health
        
    except Exception as e:
        logger.error(f"Error checking model health: {str(e)}")
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'error',
            'error': str(e),
        }


def retrain_if_needed() -> Dict[str, bool]:
    """
    Check and retrain models if needed.
    
    Returns:
        Retraining status for each model
    """
    logger.info("Checking if models need retraining")
    
    try:
        orchestrator = get_orchestrator()
        needs_retrain = orchestrator.check_retraining_needed()
        
        # Check if any need retraining
        if not any(needs_retrain.values()):
            logger.info("All models are up to date")
            return {k: False for k in needs_retrain.keys()}
        
        # Retrain those that need it
        logger.info(f"Retraining needed for: {[k for k, v in needs_retrain.items() if v]}")
        
        # Fetch fresh training data
        training_data = fetch_training_data()
        prepared_data = prepare_training_data(training_data)
        
        # Retrain only models that need it
        results = {}
        for agent_name, needs in needs_retrain.items():
            if needs:
                agent = orchestrator.agents[agent_name]
                try:
                    agent.train(prepared_data)
                    results[agent_name] = True
                    logger.info(f"✓ {agent_name} retrained successfully")
                except Exception as e:
                    logger.error(f"✗ {agent_name} retraining failed: {str(e)}")
                    results[agent_name] = False
            else:
                results[agent_name] = False
        
        return results
        
    except Exception as e:
        logger.error(f"Error during retraining check: {str(e)}")
        raise
