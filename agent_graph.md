
---
# Agent Graph & System Design Documentation

## Overview

This project implements a modular Agentic Marketing Analytics System that ingests advertising performance data, computes metrics, generates insights, produces hypotheses, validates and evaluates them, creates improved creatives, and outputs a complete marketer-ready final report.

Each agent operates independently, produces structured JSON, and passes its output into the next stage of the pipeline. The system is deterministic, observable, and fully traceable.

---

## Agent Graph (Data Flow)

```mermaid
flowchart TD

    A[User Query] --> B[Planner Agent]

    B --> C[Data Agent]
    C --> D[Insight Agent]
    D --> E[Hypothesis Agent]
    E --> F[Validator Agent]
    E --> G[Evaluator Agent]

    D --> H[Creative Improvement Agent]

    F --> I[Report Agent]
    G --> I
    H --> I

    I --> J[final_report.md]
    D --> K[insights.json]
    E --> L[hypotheses.json]
    F --> M[validated_hypotheses.json]
    G --> N[evaluated_hypotheses.json]
    H --> O[creative_recommendations.json]
````

---

## Agent Roles

### 1. Planner Agent

Plans the full execution sequence based on the user query.
Defines the following stages:

* Load dataset
* Compute metrics
* Generate insights
* Generate hypotheses
* Validate hypotheses
* Evaluate hypotheses
* Generate creative improvements
* Produce final report

Outputs a step-by-step execution plan.

---

### 2. Data Agent

Loads and processes the dataset, producing all foundational performance metrics.

Computes:

* CTR, CPC, CPM, ROAS
* Audience-level statistics
* Country-level statistics
* Platform-level statistics
* Creative fatigue indicators
* Top-performing and worst-performing creatives

Outputs: **metrics (dict)**.

---

### 3. Insight Agent

Transforms metrics into actionable insights.

Produces:

* Summary text
* 3–8 actionable insights
* Evidence per insight:

  * KPI trends
  * Creative issues
  * Audience issues
* Severity and confidence scoring

Outputs: **insights.json**.

---

### 4. Hypothesis Agent

Converts insights into structured hypotheses.

Each hypothesis includes:

* Issue
* Hypothesis statement
* Supporting signals
* Confidence score

Outputs: **hypotheses.json**.

---

### 5. Validator Agent

Validates and critiques hypotheses qualitatively.

For each hypothesis:

* Status: validated / rejected / partial
* Strengthened reasoning
* Confidence

Outputs: **validated_hypotheses.json**.

---

### 6. Evaluator Agent

Runs quantitative evaluation on hypotheses.

Adds:

* quantitative_support
* strength_score
* final confidence

Outputs: **evaluated_hypotheses.json**.

---

### 7. Creative Improvement Agent

Generates improved creatives for weak or fatigued messages.

Produces:

* issue
* old_message
* new_creative
* reasoning
* expected CTR lift

Outputs: **creative_recommendations.json**.

---

### 8. Report Agent

Builds the final, human-readable **Markdown marketing report**.

Integrates:

* metrics
* insights
* hypotheses
* validated hypotheses
* evaluated hypotheses
* creative recommendations

Outputs: **final_report.md**.

---

## File Outputs (Deliverables)

| File                          | Description                     |
| ----------------------------- | ------------------------------- |
| insights.json                 | Generated insights              |
| hypotheses.json               | Hypotheses from InsightAgent    |
| validated_hypotheses.json     | Validator results               |
| evaluated_hypotheses.json     | Evaluator results               |
| creative_recommendations.json | Improved creative suggestions   |
| final_report.md               | Final marketing analysis report |
| agent_graph.md                | System design and pipeline flow |

---

## Architecture Summary

The system is built around a deterministic linear multi-agent pipeline.
Every agent:

* accepts structured JSON
* produces structured JSON
* includes retries and validation
* logs all operations
* writes outputs to `/reports`

This ensures reproducibility, modularity, and full traceability across all stages of the analytics process.




