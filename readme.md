# Agentic Facebook Ads Analyst

Automated insights, hypotheses, validation, creative optimization, and final reporting using a multi-agent system.

## Overview

This project implements a modular agentic marketing analytics system that analyzes Facebook Ads performance end-to-end.  
It produces:

- Structured insights  
- Testable hypotheses  
- Quantitative validation  
- Creative recommendations  
- Final consolidated report  
- JSON logs for observability  

The system uses:

- Python 3.10+  
- Gemini 2.0 flash API  
- Deterministic config and reproducible pipeline  

## Quick Start

### 1. Clone the Repository

```
git clone https://github.com/<your-username>/kasparro-agentic-fb-analyst-kunal-singh.git
cd kasparro-agentic-fb-analyst-kunal-singh
```

### 2. Install Dependencies

```
pip install -r requirements.txt
```

### 3. Add Your Gemini API Key

Edit:

```
utils/gemini_client.py
```

Replace:

```
api_key="place api key here please"
```

### 4. Run the Full Pipeline

**Default run:**

```
python src/run.py
```

**Custom query:**

```
python src/run.py "Analyze ROAS drop and creative fatigue"
```

### 5. Outputs Generated In:

- `reports/`
- `logs/`

## Folder Structure

```
├── README.md
├── requirements.txt
├── config/
│   ├── config.yaml
├── data/
│   ├── synthetic_fb_ads_undergarments.csv
│   ├── README.md
├── src/
│   ├── agents/
│   ├── orchestrator/
│   ├── utils/
│   ├── run.py
├── logs/
├── reports/
├── tests/
```

## Features

- Planner Agent  
- Data Agent  
- Insight Agent  
- Hypothesis Agent  
- Validator Agent  
- Evaluator Agent  
- Creative Improvement Agent  
- Report Agent  
- Central logging system  

