
# Agentic Facebook Ads Analyst

Automated insights, hypotheses, validation, creative optimization, and final reporting using a modular multi-agent analytics system.
---
### Agent Graph  
[📄 Open agent_graph.md](https://github.com/kunal-kumar-singh07/kasparro-agentic-fb-analyst-kunal-singh/blob/main/reports/agent_graph.md)

---

---

## Overview

This project implements a complete, agent-driven marketing analytics pipeline designed to analyze Facebook Ads performance end-to-end.

The pipeline produces:

* Structured insights
* Testable hypotheses
* Quantitative validation
* Creative improvement recommendations
* Consolidated markdown reports
* JSON logs and metrics for observability

Technologies used:

* Python 3.10+
* Gemini 2.0 Flash API
* Multi-agent modular architecture
* Configuration-driven execution

---

## Direct Download

Download ZIP:

**[https://github.com/kunal-kumar-singh07/kasparro-agentic-fb-analyst-kunal-singh/archive/refs/heads/main.zip](https://github.com/kunal-kumar-singh07/kasparro-agentic-fb-analyst-kunal-singh/archive/refs/heads/main.zip)**

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

### 3. Configure Your Gemini API Key

Open:

```
utils/gemini_client.py
```

Set:

```
api_key = "YOUR_API_KEY"
```

### 4. Run the Pipeline

Default:

```
python src/run.py
```

With custom query:

```
python src/run.py "Analyze ROAS drop and creative fatigue"
```

---

## Running With Makefile (Optional)

A Makefile is included for simplified execution.

### Run default pipeline:

```
make run
```

### Run with custom query:

```
make run-query QUERY="Why did ROAS drop last week?"
```

### Install requirements:

```
make install
```

### Clean results/logs:

```
make clean
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
│   │   ├── data_agent.py
│   │   ├── insight_agent.py
│   │   ├── hypothesis_agent.py
│   │   ├── evaluator_agent.py
│   │   ├── validator_agent.py
│   │   ├── creative_agent.py
│   │   └── report_agent.py
│   ├── utils/
│   ├── orchestrator/
│   └── run.py
```

---

## Features

* Planner Agent for execution strategy
* Data Agent for metrics computation
* Insight Agent for evidence extraction
* Hypothesis Agent for generating testable hypotheses
* Evaluator Agent for quantitative scoring
* Validator Agent for reasoning refinement
* Creative Agent for generating improved ad messaging
* Report Agent for final markdown reporting
* Full logging and result tracking system

---
