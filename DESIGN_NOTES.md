# Design Notes (V2 Upgrade)

This document outlines the engineering improvements delivered in the V2 refactor of the Agentic Facebook Ads Analytics System.  
The objective of this iteration was to strengthen reliability, observability, modularity, and production readiness without increasing system complexity.

---

## 1. High-Level Upgrade Summary

### 1.1 Unified `BaseAgent` Architecture  
All LLM-powered agents now inherit from a single shared base class. This standardization consolidates:

- retry logic  
- prompt assembly  
- LLM call handling  
- JSON extraction (strict → regex → cleanup)  
- fallback behavior  
- metadata construction  
- structured logging  

This eliminates approximately 70% of duplicated logic and ensures uniform behavior across all agents.

### 1.2 Enhanced Error Handling  
Agents now share robust fault-tolerant patterns:

- automatic retries with incremental backoff  
- clear error categories (`llm_api_failure`, `json_parse_error`, `agent_fallback`)  
- prompt regeneration for malformed model outputs  
- guaranteed fallback structures to maintain pipeline continuity  

### 1.3 Improved Observability  
A lightweight metrics tracker was added to capture:

- agent-level latency  
- number of LLM calls  
- stage-level timestamps  
- operational counters (rows processed, retries, errors)  
- total runtime for the entire run  

A consolidated metrics JSON file is produced for every execution.

### 1.4 Structured Logging  
The system uses a unified JSONL log schema through `log_event()`:

- run_id  
- agent name  
- event type  
- payload  
- timestamp  

This allows deterministic replay of the entire pipeline and fast debugging of failure points.

### 1.5 Configuration & Security Hygiene  
All operational settings are now sourced from:

- `config/config.yaml`  
- environment variable overrides  

No hardcoded paths, thresholds, or API keys.  
This improves portability and prepares the project for cloud environments.

### 1.6 Expanded Test Coverage  
Tests now include:

- `DataAgent` unit tests  
- Evaluator logic tests  
- Deterministic LLM mocks  
- End-to-end integration test covering  
  **metrics → insights → hypotheses → evaluation → validation → reporting**

This ensures stability and repeatability across versions.

---

## 2. Improvements by Component

### BaseAgent
- deterministic life cycle  
- unified retries, LLM calls, and JSON parsing  
- structured fallback logic  
- integrated latency and call-count tracking  
- consistent metadata generation  

### DataAgent
- safer type coercion  
- threshold-driven fatigue detection  
- configuration-powered behavior  

### InsightAgent
- cleaner schema  
- predictable JSON layouts  
- improved prompt clarity  

### HypothesisAgent
- strengthened structure  
- improved supporting-signal extraction  
- consistent confidence scoring  

### EvaluatorAgent
- clearer scoring schema  
- improved quantitative reasoning  
- added debugging counters for hypothesis scoring  

### ValidatorAgent
- stronger hypothesis refinement  
- consistent validity classifications  
- stabilized output schema  

### CreativeImprovementAgent
- simplified logic  
- cleaner schema adherence  
- predictable JSON responses  

### ReportAgent
- clean Markdown generation pipeline  
- isolation between JSON text and Markdown output  
- improved breakdown of full pipeline results  

---

## 3. Future Opportunities (If More Time Were Available)

### 3.1 Adaptive Intelligence  
- dynamic hypothesis depth based on dataset size  
- adaptive evaluator confidence scoring  
- planner that conditionally enables/disables agents depending on the data  

### 3.2 Enhanced Reporting  
- visual charts (ROAS, CTR, CPM)  
- creative clustering and fatigue visualizations  
- optional HTML or PDF report export  

### 3.3 Operational Extensions  
- incremental run caching  
- checkpointed pipeline stages  
- Dockerization and cloud deployment profile  
- environment-specific config (dev/stage/prod)  

---

## 4. Conclusion

The V2 upgrade refines the system into a robust, production-ready analytics platform with:

- strong abstractions  
- comprehensive error handling  
- consistent agent behavior  
- improved observability  
- safer configuration  
- measurable and testable outputs  

These enhancements significantly elevate the engineering quality and prepare the system for real-world, iterative use.
