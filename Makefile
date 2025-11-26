PYTHON=python
MAIN=src/run.py

run:
	@echo " Running Agentic FB Ads Analytics Pipeline..."
	$(PYTHON) $(MAIN)

run-query:
	@echo "Running Pipeline With Custom Query..."
	$(PYTHON) $(MAIN) $(QUERY)
