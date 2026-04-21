PYTHON ?= python

.PHONY: install crawl import-graph run-api compile

install:
	$(PYTHON) -m pip install -r requirements.txt

crawl:
	$(PYTHON) -m data_pipeline

import-graph:
	$(PYTHON) scripts/import_neo4j.py

run-api:
	uvicorn job_kg.api:app --reload

compile:
	$(PYTHON) -m compileall job_kg data_pipeline scripts
