# AI Agent System Documentation
# =============================

## Overview

The PASE Monitor Portal now includes a sophisticated AI Agent System for **predictive analytics** and **intelligent monitoring** of Informatica jobs.

## 🤖 AI Agents

### 1. **Anomaly Detection Agent**
- **Technology**: Isolation Forest + Statistical Analysis
- **Purpose**: Identifies unusual patterns in job execution
- **Detects**:
  - Unusual runtime durations
  - Unexpected failure patterns
  - Abnormal resource usage
  - Irregular scheduling patterns

### 2. **Predictive Failure Analysis Agent**
- **Technology**: Random Forest + Gradient Boosting ensemble
- **Purpose**: Predicts job failures before they occur
- **Provides**:
  - Failure probability scores (0-1)
  - Risk levels (CRITICAL, HIGH, MEDIUM, LOW)
  - Root cause indicators
  - Confidence scores

### 3. **Pattern Identification Agent**
- **Technology**: K-Means + DBSCAN clustering
- **Purpose**: Discovers patterns and trends in execution
- **Identifies**:
  - Job groupings and dependencies
  - Temporal execution patterns
  - Performance trends
  - Outlier behaviors

### 4. **Alert & Recommendation Agent**
- **Technology**: Rule-based + Priority Scoring
- **Purpose**: Generates intelligent alerts and recommendations
- **Provides**:
  - Prioritized alerts (by business impact)
  - Actionable recommendations
  - Alert deduplication
  - Executive summaries

## 📊 Features Engineered

The system generates **50+ features** from raw job data:

### Temporal Features
- Hour of day, day of week, month
- Is weekend, is business hours
- Shift classification (morning/afternoon/evening/night)
- Cyclical encoding (sin/cos) for periodicity

### Runtime Features
- Duration statistics (mean, median, std, percentiles)
- Per-job duration baselines
- Deviation from normal runtime
- Duration categories

### Historical Features
- Failure counts (last 5, 10, 24 runs)
- Success rates (rolling windows)
- Consecutive failure streaks
- Days since last failure
- Time between runs

### Statistical Features
- Rolling means/stds (5h, 10h, 24h, 7d windows)
- Z-scores (local and global)
- Exponential moving averages
- Min/max within windows

### Business Context Features
- Application categorization
- Job complexity indicators
- Business impact scores
- Priority calculations

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
cd monitorportal
.venv\Scripts\activate

# Install AI packages
pip install numpy pandas scikit-learn
```

### 2. Train Models (First Time)

```bash
# Train all models on 90 days of historical data
python manage.py train_ai_models

# Or specify custom lookback period
python manage.py train_ai_models --lookback-days 180
```

Training takes **5-10 minutes** depending on data volume.

### 3. Access AI Dashboard

1. Start the Django server: `python manage.py runserver`
2. Navigate to: http://localhost:8000/ai/
3. Click **"Run Analysis"** to get insights

## 📡 API Endpoints

### Analysis Endpoints

```python
GET  /ai/api/insights/          # Get high-level summary
GET  /ai/api/anomalies/         # Get anomaly detection results
GET  /ai/api/predictions/       # Get failure predictions
GET  /ai/api/patterns/          # Get pattern analysis
GET  /ai/api/alerts/            # Get alerts & recommendations
POST /ai/api/run-analysis/      # Run new analysis
```

### Management Endpoints

```python
POST /ai/api/train/             # Train all models
POST /ai/api/load/              # Load pre-trained models
GET  /ai/api/health/            # Check model health
POST /ai/api/retrain/           # Retrain if needed
GET  /ai/api/status/            # Get agent status
GET  /ai/api/system-health/     # Complete system health
```

## 💻 Command Line Usage

### Run One-Time Analysis

```bash
python manage.py run_ai_analysis
```

### Run Continuous Analysis (Background Mode)

```bash
# Run every 15 minutes
python manage.py run_ai_analysis --continuous

# Custom interval (30 minutes)
python manage.py run_ai_analysis --continuous --interval 30

# Analyze specific application
python manage.py run_ai_analysis --application level3 --continuous
```

### Train/Retrain Models

```bash
# Initial training
python manage.py train_ai_models

# Retrain with more history
python manage.py train_ai_models --lookback-days 180
```

## 🔧 Configuration

Edit `portal/ai/config.py` to customize:

### Model Parameters

```python
ANOMALY_DETECTION_CONFIG = {
    'isolation_forest': {
        'contamination': 0.1,      # Expected % of outliers
        'n_estimators': 100,       # Number of trees
    },
}

PREDICTIVE_FAILURE_CONFIG = {
    'threshold': 0.7,              # Failure prediction threshold
    'random_forest': {
        'n_estimators': 200,       # Number of trees
        'max_depth': 20,
    },
}
```

### Alert Thresholds

```python
ALERT_RECOMMENDER_CONFIG = {
    'alert_thresholds': {
        'critical': 0.8,           # Score >= 0.8 = CRITICAL
        'high': 0.6,               # Score >= 0.6 = HIGH
        'medium': 0.4,             # etc.
        'low': 0.2,
    },
}
```

### Execution Settings

```python
EXECUTION_CONFIG = {
    'update_frequency_minutes': 15,  # Cache refresh interval
    'model_retrain_days': 7,         # Retrain every N days
    'lookback_days': 90,             # Training data window
}
```

## 📈 Usage Example

### Python API

```python
from portal.ai.orchestrator import get_orchestrator
from portal.ai.training import train_all_models
import pandas as pd

# Train models (first time)
train_all_models(lookback_days=90)

# Get orchestrator
orchestrator = get_orchestrator()

# Fetch and analyze all applications
results = orchestrator.fetch_and_analyze(application='all')

# Access specific results
anomalies = results['anomaly_detection']
predictions = results['predictive_failure']
patterns = results['pattern_identification']
alerts = results['alerts_recommendations']

# Get executive summary
summary = results['summary']
print(summary['executive_summary'])
print(f"Critical Alerts: {summary['key_metrics']['critical_alerts']}")
```

### JavaScript (Frontend)

```javascript
// Run analysis
const response = await fetch('/ai/api/run-analysis/');
const result = await response.json();

// Get insights
const insights = await fetch('/ai/api/insights/');
const data = await insights.json();

console.log(data.data.executive_summary);
console.log(`Anomalies: ${data.data.anomalies.count}`);
console.log(`Predicted Failures: ${data.data.predictions.predicted_failures}`);
```

## 🎯 Key Metrics

The AI system provides real-time insights on:

- **Anomaly Rate**: % of jobs showing unusual behavior
- **Failure Probability**: Risk score (0-1) for each job
- **Pattern Distribution**: Job groupings and execution patterns
- **Alert Priority**: CRITICAL/HIGH/MEDIUM/LOW
- **Confidence Scores**: Model certainty in predictions

## 🔄 Model Lifecycle

### 1. Training (Initial)
- Fetch 90 days of historical data
- Engineer 50+ features
- Train 4 specialized models
- Save models to disk

### 2. Inference (Real-time)
- Load pre-trained models
- Fetch current job data
- Apply feature engineering
- Run all 4 agents
- Generate insights & alerts

### 3. Retraining (Periodic)
- Check model age (default: 7 days)
- Fetch fresh historical data
- Retrain aged models
- Update model files

## 📁 File Structure

```
portal/
├── ai/
│   ├── __init__.py
│   ├── config.py                    # Configuration
│   ├── base_agent.py                # Base agent class
│   ├── orchestrator.py              # Main orchestrator
│   ├── feature_engineering.py       # Feature pipeline
│   ├── training.py                  # Training utilities
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── anomaly_detector.py      # Agent 1
│   │   ├── predictive_failure.py    # Agent 2
│   │   ├── pattern_identifier.py    # Agent 3
│   │   └── alert_recommender.py     # Agent 4
│   ├── models/                      # Saved ML models
│   ├── data/                        # Cached data
│   └── logs/                        # AI system logs
├── ai_views.py                      # Django views/APIs
├── management/
│   └── commands/
│       ├── train_ai_models.py       # Training command
│       └── run_ai_analysis.py       # Analysis command
└── templates/
    └── portal/
        └── ai_dashboard.html         # Dashboard UI
```

## 🧪 Testing

### Test Individual Agents

```python
from portal.ai.agents.anomaly_detector import AnomalyDetectorAgent
import pandas as pd

# Create sample data
data = pd.DataFrame({
    'job_name': ['Job1', 'Job2'],
    'duration_seconds': [100, 5000],
    'start_time': ['2024-01-01 10:00', '2024-01-01 11:00'],
    'status': ['SUCCESS', 'FAILED']
})

# Create and train agent
agent = AnomalyDetectorAgent()
agent.train(data)

# Make predictions
predictions = agent.predict(data)
print(predictions[['job_name', 'is_anomaly', 'anomaly_score']])
```

### Test Orchestrator

```python
from portal.ai.orchestrator import get_orchestrator

orchestrator = get_orchestrator()

# Check status
status = orchestrator.get_agent_status()
print(status)

# Get insights
insights = orchestrator.get_insights_summary()
print(insights)
```

## 🚨 Troubleshooting

### Models Not Trained

**Error**: `RuntimeError: Model not trained`

**Solution**:
```bash
python manage.py train_ai_models
```

### No Data Available

**Error**: `ValueError: No data available from any source`

**Solution**: Ensure Oracle databases are accessible and contain data

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'sklearn'`

**Solution**:
```bash
pip install scikit-learn pandas numpy
```

### Slow Training

**Issue**: Training takes too long

**Solution**: Reduce lookback period:
```bash
python manage.py train_ai_models --lookback-days 30
```

## 📊 Performance

- **Training Time**: 5-10 minutes (90 days of data)
- **Inference Time**: < 5 seconds per analysis
- **Memory Usage**: ~500MB (loaded models)
- **Disk Space**: ~50MB (saved models)

## 🔜 Future Enhancements

Potential additions:

1. **Deep Learning**: LSTM networks for time-series forecasting
2. **Real-time Alerts**: Email/Slack notifications
3. **Auto-remediation**: Automatic job restarts
4. **Explainable AI**: SHAP values for predictions
5. **Model Monitoring**: Performance metrics tracking
6. **A/B Testing**: Compare model versions

## 📝 Notes

- Models are persisted in `portal/ai/models/`
- Logs are written to `portal/ai/logs/ai_system.log`
- Cache expires every 15 minutes (configurable)
- All agents use ensemble methods for robustness

## 🎓 Technical Details

### Machine Learning Models

1. **Isolation Forest**: Unsupervised anomaly detection
2. **Random Forest**: Supervised classification (failures)
3. **Gradient Boosting**: Boosted classification
4. **K-Means**: Unsupervised clustering
5. **DBSCAN**: Density-based clustering

### Feature Engineering Techniques

- **Temporal encoding**: Cyclical features for periodicity
- **Rolling statistics**: Window-based aggregations
- **Z-score normalization**: Outlier detection
- **Lag features**: Historical job performance
- **Domain features**: Business context

### Ensemble Strategy

All prediction agents use **ensemble methods**:
- Multiple models vote on predictions
- Average probabilities for robustness
- Confidence based on model agreement

---

**For questions or issues, check the logs at `portal/ai/logs/ai_system.log`**
