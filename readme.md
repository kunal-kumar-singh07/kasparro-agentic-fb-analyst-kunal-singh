
# Agentic Facebook Ads Analyst

A modular, multi-agent analytics system for automated Facebook Ads insights, hypothesis generation, evaluation, validation, creative optimization, and final reporting.  
Designed with clean architecture, strong observability, and comprehensive testing.

---
## Documentation

[▶ View Agent Graph](agent_graph.md)

[▶ View Design Notes](DESIGN_NOTES.md)


---

## Overview

This system performs a complete end-to-end analysis of Facebook Ads performance using multiple specialized agents.

The pipeline:

1. Loads and cleans source data  
2. Computes key marketing KPIs  
3. Generates insights from metrics  
4. Produces testable hypotheses  
5. Quantitatively evaluates hypotheses  
6. Validates them for logical soundness  
7. Produces improved creatives  
8. Generates a clean final Markdown report  

Technologies used:

- Python 3.10+
- Gemini 2.0 Flash API
- Multi-agent modular architecture
- Configuration-driven execution
- Structured logging and metrics for observability

---

## Download

Repository ZIP:  
https://github.com/kunal-kumar-singh07/kasparro-agentic-fb-analyst-kunal-singh/archive/refs/heads/main.zip

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/kunal-kumar-singh07/kasparro-agentic-fb-analyst-kunal-singh.git
cd kasparro-agentic-fb-analyst-kunal-singh
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Gemini API key

Open:

```text
utils/gemini_client.py
```

Set:

```python
api_key = "YOUR_API_KEY"
```

### 4. Run the pipeline

Default run:

```bash
python src/run.py
```

Custom query:

```bash
python src/run.py "Why did ROAS drop this week?"
```

---

## Makefile (optional)

Run default pipeline:

```bash
make run
```

Run with query:

```bash
make run-query QUERY="Analyze CTR drop"
```

Install dependencies:

```bash
make install
```

Clean results/logs:

```bash
make clean
```

---

## Project Structure

Top level:

```text
├── DESIGN_NOTES.md
├── README.md
├── Makefile
├── requirements.txt
├── config/
│   └── config.yaml
├── data/
│   └── sample_facebook_ads.csv
├── logs/
├── reports/
├── src/
└── utils/
```

Inside `src/`:

```text
src/
├── agents/
│   ├── base_agent.py
│   ├── data_agent.py
│   ├── insight_agent.py
│   ├── hypothesis_agent.py
│   ├── evaluator_agent.py
│   ├── validator_agent.py
│   ├── creative_agent.py
│   ├── report_agent.py
│   └── planner_agent.py
├── logs/
├── prompts/
│   ├── insight_agent.md
│   ├── hypothesis_agent.md
│   ├── evaluator_agent.md
│   ├── validator_agent.md
│   ├── creative_agent.md
│   └── report_agent.md
├── results/
│   └── (intermediate JSON outputs written here)
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── fake_llm.py
│   ├── test_data_agent.py
│   ├── test_insight_agent.py
│   ├── test_hypothesis_agent.py
│   ├── test_evaluator_agent.py
│   ├── test_evaluator_logic.py
│   └── test_integration_flow.py
├── __init__.py
├── final_report.md           (example output from a run)
├── report_raw_debug.txt      (debug/raw report capture)
└── run.py
```

Inside `utils/`:

```text
utils/
├── __init__.py
├── gemini_client.py
├── ollama_client.py
├── logging_utils.py
├── logger.py
└── metrics.py
```

---

## Agents Overview

### PlannerAgent

Creates the full execution plan for the pipeline (order of agents and their responsibilities).

### DataAgent

Loads CSV data, normalizes schema, and computes key metrics:

* CTR
* ROAS
* CPC
* CPM
* daily trends
* creative fatigue signals
* top and worst creatives

### InsightAgent

Analyzes metrics and generates structured insights with evidence and severity.

### HypothesisAgent

Converts insights into clear, testable hypotheses with supporting signals and confidence.

### EvaluatorAgent

Uses quantitative signals to evaluate each hypothesis and assign strength and confidence scores.

### ValidatorAgent

Validates, critiques, and strengthens hypotheses, marking them as validated, rejected, or partial.

### CreativeImprovementAgent

Generates 5–8 improved creative ad variations, each with:

* issue
* old_message
* new_creative
* reasoning
* expected_ctr_lift

### ReportAgent

Produces a final, business-ready Markdown report combining metrics, insights, hypotheses, validations, and creative recommendations.

---

## Observability and Metrics

The system tracks:

* Stage timestamps
* Agent-level latency
* Total runtime
* LLM call counts
* Rows processed
* Pipeline stage durations

Example `pipeline_metrics.json`:

```json
{
  "run_id": "f046da75c1",
  "counters": { "rows_processed": 4500 },
  "stages": {
    "metrics_ready": 1764530752.7099,
    "insights_ready": 1764530758.9315,
    "hypotheses_ready": 1764530762.4983,
    "evaluation_ready": 1764530767.5331,
    "validated_ready": 1764530771.1253,
    "creatives_ready": 1764530777.0670,
    "report_ready": 1764530789.3678
  },
  "durations": {
    "metrics_ready_to_insights_ready": 6.222,
    "insights_ready_to_hypotheses_ready": 3.567,
    "hypotheses_ready_to_evaluation_ready": 5.035,
    "evaluation_ready_to_validated_ready": 3.592,
    "validated_ready_to_creatives_ready": 5.942,
    "creatives_ready_to_report_ready": 12.301
  },
  "times": {
    "total_runtime": 36.692
  }
}
```

---

## Security Practices

* No hardcoded API keys
* LLM keys loaded via environment or config
* Clean configuration via `config.yaml`
* Environment-based overrides supported
* No sensitive user data logged

---

## Testing

Tests cover:

* BaseAgent behavior (retries, fallback, JSON parsing)
* DataAgent loading and metric computation
* InsightAgent, HypothesisAgent, EvaluatorAgent, ValidatorAgent, CreativeImprovementAgent
* Integration flow:

  * metrics → insights → hypotheses → evaluation → validation → creative recommendations
* LLM failure simulations (invalid JSON, retries, fallbacks)

Run tests with:

```bash
pytest -q
```

---

## Design Notes (V2 Upgrade)

See `DESIGN_NOTES.md` for a detailed description of:

* What changed in this iteration (error handling, logging, tests, security, configs)
* How the BaseAgent unifies agent behavior
* Observability design (metrics + logs)
* What would be done next with more time (adaptive thresholds, smarter planner, charts, Docker, etc.)

---

## Example Reports

The final Markdown report includes:

* Executive summary
* KPI overview
* ROAS trend
* Insights
* Hypotheses
* Hypothesis evaluations and validations
* Creative recommendations
* Strategic next steps

Output is written to:

```text
results/final_report.md
```

---

## License

MIT License


