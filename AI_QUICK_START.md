# 🤖 AI Agent System - Quick Start Guide

## ✅ Installation Complete!

The AI Agent System has been successfully integrated into your PASE Monitor Portal!

## 🚀 Getting Started (3 Steps)

### Step 1: Train the AI Models (First Time Only)

Open a terminal in the `monitorportal` directory and run:

```bash
python manage.py train_ai_models
```

This will:
- Fetch 90 days of historical job data
- Engineer 50+ predictive features
- Train 4 specialized AI agents
- Save models for future use

⏱️ **Time**: 5-10 minutes
💾 **Disk Space**: ~50MB for models

### Step 2: Start the Django Server

```bash
python manage.py runserver
```

### Step 3: Access AI Dashboard

Open your browser and go to:
```
http://localhost:8000/ai/
```

Click the **"Run Analysis"** button to see AI insights!

---

## 🎯 What You Get

### 🔍 Anomaly Detection
- Identifies unusual job behaviors
- Detects runtime deviations
- Flags abnormal patterns

### 🎯 Failure Predictions
- Predicts which jobs are at risk
- Provides probability scores (0-100%)
- Risk levels: CRITICAL, HIGH, MEDIUM, LOW

### 📊 Pattern Discovery
- Groups similar jobs together
- Identifies execution trends
- Detects outliers

### 🚨 Smart Alerts
- Prioritized by business impact
- Actionable recommendations
- Automatic deduplication

---

## 📊 Dashboard Features

### Key Metrics Cards
- **Anomalies Detected**: Count and rate
- **Predicted Failures**: At-risk jobs
- **Patterns Identified**: Job groupings
- **Active Alerts**: Critical/High/Medium/Low

### Interactive Tabs
1. **Overview**: Executive summary & top recommendations
2. **Anomalies**: Detailed anomaly analysis
3. **Predictions**: Failure risk breakdown
4. **Patterns**: Pattern visualizations
5. **Alerts**: All alerts with priorities
6. **Agent Status**: Model health & training status

---

## 💻 Command Line Tools

### Run Analysis

```bash
# One-time analysis
python manage.py run_ai_analysis

# Continuous monitoring (every 15 minutes)
python manage.py run_ai_analysis --continuous

# Custom interval (30 minutes)
python manage.py run_ai_analysis --continuous --interval 30

# Specific application
python manage.py run_ai_analysis --application level3
```

### Model Management

```bash
# Train all models
python manage.py train_ai_models

# Train with custom history
python manage.py train_ai_models --lookback-days 180

# Check model health (via Python)
python -c "from portal.ai.training import check_model_health; print(check_model_health())"
```

---

## 🔗 API Integration

### Get Insights (JSON)

```bash
# Get summary
curl http://localhost:8000/ai/api/insights/

# Get anomalies
curl http://localhost:8000/ai/api/anomalies/

# Get predictions
curl http://localhost:8000/ai/api/predictions/

# Get alerts
curl http://localhost:8000/ai/api/alerts/
```

### Run Analysis via API

```bash
curl -X POST http://localhost:8000/ai/api/run-analysis/
```

---

## ⚙️ Configuration

Edit `portal/ai/config.py` to customize:

### Alert Thresholds
```python
'alert_thresholds': {
    'critical': 0.8,  # 80% probability = CRITICAL
    'high': 0.6,      # 60% probability = HIGH
    'medium': 0.4,
    'low': 0.2,
}
```

### Analysis Frequency
```python
'update_frequency_minutes': 15,  # Cache refresh interval
'model_retrain_days': 7,         # Auto-retrain every week
```

---

## 🎨 Navigation

The AI Dashboard is accessible from:
1. **Main navigation bar**: Click "🤖 AI INSIGHTS"
2. **Direct URL**: http://localhost:8000/ai/
3. **Home page**: (add link if desired)

---

## 🔧 Troubleshooting

### Problem: "RuntimeError: No trained model available"
**Solution**: Train the models first:
```bash
python manage.py train_ai_models
```

### Problem: "No data available from any source"
**Solution**: Ensure Oracle databases are accessible and contain data

### Problem: Analysis takes too long
**Solution**: The first run trains models. Subsequent runs use cached models and are faster.

### Problem: Import errors
**Solution**: Verify all packages are installed:
```bash
pip install numpy pandas scikit-learn
```

---

## 📈 Example Output

After running analysis, you'll see:

```
Key Metrics:
  - Anomalies: 12 (8.5% anomaly rate)
  - Predicted Failures: 5 jobs at HIGH/CRITICAL risk
  - Critical Alerts: 2
  - High Alerts: 8

Executive Summary:
⚠️ WARNING: Elevated risk levels detected. 5 jobs at risk of failure.

Top Recommendations:
  1. ⚠️ 2 jobs showing repeated failures. Immediate investigation required.
  2. Check resource allocation for 3 jobs with unusual runtimes.
  3. Review scheduling for jobs running outside business hours.
```

---

## 🎓 Understanding Results

### Anomaly Score
- **Lower is MORE anomalous** (e.g., -0.8 is very unusual)
- Scores < -0.5: Likely anomaly
- Scores > 0: Normal behavior

### Failure Probability
- **0.0 - 0.2**: MINIMAL risk (0-20% chance of failure)
- **0.2 - 0.4**: LOW risk
- **0.4 - 0.6**: MEDIUM risk
- **0.6 - 0.8**: HIGH risk
- **0.8 - 1.0**: CRITICAL risk (80-100% chance of failure)

### Risk Levels
- **CRITICAL**: Immediate action required
- **HIGH**: Review within 24 hours
- **MEDIUM**: Monitor closely
- **LOW**: Informational

---

## 📚 Advanced Usage

### Python Integration

```python
from portal.ai.orchestrator import get_orchestrator

# Get orchestrator
orchestrator = get_orchestrator()

# Run analysis
results = orchestrator.fetch_and_analyze()

# Access results
print(results['summary']['executive_summary'])
print(f"Anomalies: {results['anomaly_detection']['anomalies_detected']}")
print(f"At-risk jobs: {results['predictive_failure']['predicted_failures']}")
```

### Custom Analysis

```python
from portal.ai.agents.anomaly_detector import AnomalyDetectorAgent
import pandas as pd

# Load your data
df = pd.DataFrame({...})

# Create agent
agent = AnomalyDetectorAgent()

# Train (if needed)
agent.train(df)

# Analyze
results = agent.analyze(df)
print(results)
```

---

## 🔮 What's Next?

1. **Train Models**: Run `python manage.py train_ai_models`
2. **Explore Dashboard**: Visit http://localhost:8000/ai/
3. **Run Analysis**: Click "Run Analysis" button
4. **Review Alerts**: Check the Alerts tab for recommendations
5. **Set Up Continuous Monitoring**: Use `--continuous` flag

---

## 📖 Full Documentation

For complete details, see: **AI_SYSTEM_README.md**

---

## 🎉 You're Ready!

The AI Agent System is now enhancing your PASE Monitor Portal with:
- ✅ Real-time anomaly detection
- ✅ Predictive failure analysis
- ✅ Pattern discovery
- ✅ Intelligent alerting
- ✅ Automated recommendations

**Start by training the models, then explore the AI Dashboard!**

```bash
python manage.py train_ai_models
python manage.py runserver
# Visit: http://localhost:8000/ai/
```

---

**Questions?** Check logs at: `portal/ai/logs/ai_system.log`
