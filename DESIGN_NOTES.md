# Design Notes (V2 Upgrade)

This document summarizes the engineering improvements made in the V2 refactor of the Facebook Ads Multi-Agent Analytics System.  
The goal of this upgrade was to increase reliability, maintainability, and production readiness while keeping the codebase readable and interview-friendly.

---

## 1. High-Level Upgrade Summary

### ✔ Introduced a unified BaseAgent architecture
- All LLM-based agents now inherit from a shared `BaseAgent`.
- Standardized:
  - retry logic
  - JSON parsing (flexible mode)
  - error handling
  - fallback logic
  - structured logging
  - metadata output

This reduced ~70% duplicate code across agents and made each agent predictable and easier to test.

### ✔ LLM error handling improved
- Clear exception classes (`LLMError`, `JSONParseError`, `AgentRuntimeError`)
- Auto-retries with exponential backoff
- Prompt regeneration when JSON is invalid
- Stable fallback data for downstream safety

### ✔ Improved observability
- Added lightweight `Metrics` collector:
  - counters
  - timings
  - stage timestamps
  - run_id tracking
- Pipeline writes a full `{run_id}_metrics.json` snapshot.

### ✔ Structured logs
- Every event uses `log_event()` in JSONL format  
- Logs include: run_id, agent, stage, payload, timestamps.

### ✔ Cleaner pipeline (run.py)
- Linear stage flow, no clutter
- run_id tracked across entire pipeline
- evaluator loop simplified
- consistent return shape

### ✔ Security and config hygiene
- All runtime paths + thresholds come from YAML (no hardcoded keys)
- Ready for environment-based key injection (Gemini/OpenAI keys)

### ✔ Testability improved
- Each agent now has deterministic behavior:
  - cleaner prompts
  - stable return shape
  - predictable error modes
- Shared logic moved to BaseAgent → easier to mock in tests.

---

## 2. What Was Improved in Each Agent

### BaseAgent v2
- Unified internal architecture for all LLM-based components.
- Full retry system with improved prompts.
- Flexible JSON parser with strict → regex → cleanup pipeline.
- Consistent metadata object.
- Clean short comments for readability.

### InsightAgent
- Now ~40 lines instead of ~130.
- Only contains logic specific to insight generation.
- Inherits all safety from BaseAgent.

### HypothesisAgent
- Cleaner schema, simple prompt, stable structure.

### EvaluatorAgent
- More predictable evaluation loop responses.
- Better JSON stability.

### ValidatorAgent
- Clearer validation schema.
- More consistent downstream compatibility.

### CreativeImprovementAgent
- Simplified prompts.
- Predictable JSON layout for creative recommendations.

### ReportAgent
- Special behavior for markdown handled cleanly.
- Overrode BaseAgent JSON parsing to raw text flow.

### DataAgent
- Cleaner numeric safety conversions.
- Config-driven thresholds.
- Improved fatigue detection.

---

## 3. What I Would Do Next (If Given More Time)

### 3.1. Add streaming / partial results
- Stream LLM evaluation progressively.
- Support mid-run interruption + checkpoint resume.

### 3.2. Add evaluation heatmaps / charts
- Simple matplotlib rendering inside results/ folder.
- Optional HTML export for better visualization.

### 3.3. Add more adaptive intelligence
- HypothesisAgent could adjust depth based on dataset size.
- EvaluatorAgent could tighten scoring rules based on repeated weak results.
- PlannerAgent could dynamically add/remove stages.

### 3.4. Memory of past runs
- Cache insights from previous runs to compare performance over time.

### 3.5. Containerization + Config Environments
- Add Dockerfile
- .env loader
- Staging vs Production config files

---

## 4. Summary

This V2 upgrade moves the system from a prototype into a mini-production architecture with:

- consistent internal conventions  
- unified agent lifecycle  
- strong observability  
- safer error handling  
- better separation of concerns  
- more readable, smaller code  

The project now reflects engineering maturity expected from a real-world ML platform.

