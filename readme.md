
---

# Agentic Facebook Ads Analyst

Automated insights, hypotheses, validation, creative optimization, and final reporting using a multi-agent intelligence system.

---

## Overview

This project implements a modular, agentic marketing analytics system that analyzes Facebook Ads performance end-to-end using an orchestrated multi-agent workflow.

The system automatically produces:

* Structured insights
* Testable hypotheses
* Quantitative validation
* Creative recommendations
* Final markdown report
* JSON logs for observability
* Reproducible, config-driven pipeline

Built with:

* Python 3.10+
* Gemini 2.0 Flash API
* Modular agent architecture

---

## Direct Download

Download the full project as a ZIP:

**[https://github.com/kunal-kumar-singh07/kasparro-agentic-fb-analyst-kunal-singh/archive/refs/heads/main.zip](https://github.com/kunal-kumar-singh07/kasparro-agentic-fb-analyst-kunal-singh/archive/refs/heads/main.zip)**

You can put this link directly in the README.

---

## Quick Start

### 1. Clone the Repository

```
git clone https://github.com/kunal-kumar-singh07/kasparro-agentic-fb-analyst-kunal-singh.git
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
api_key = "YOUR_API_KEY"
```

### 4. Run the Pipeline

Default run:

```
python src/run.py
```

Custom query:

```
python src/run.py "Analyze ROAS drop and creative fatigue"
```

Optional (Makefile):

```
make run
```

---

## Folder Structure

```
├── README.md
├── Makefile
├── requirements.txt
├── config/
│   └── config.yaml
├── data/
│   ├── sample_facebook_ads.csv
│   └── README.md
├── logs/
├── results/
├── reports/
├── src/
│   ├── agents/
│   ├── utils/
│   ├── orchestrator/
│   └── run.py
```

---

## Features

* Planner Agent
* Data Agent
* Insight Agent
* Hypothesis Agent
* Evaluator Agent
* Validator Agent
* Creative Improvement Agent
* Report Agent
* Central logging system
* Structured JSON outputs
* Deterministic and reproducible pipeline

---
