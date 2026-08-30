.PHONY: help install gate model artefacts viewer all clean

help:
	@echo "install    install dependencies"
	@echo "gate       ontology gate + structural contract + viewer check"
	@echo "model      rebuild ECM + MVM from the ontology"
	@echo "artefacts  DDL, DBML, metric SQL, tag taxonomy"
	@echo "viewer     refresh the viewer payload"
	@echo "all        model + artefacts + viewer + gate"

install:
	pip install -r requirements.txt

gate:
	python agent/validator.py
	python -m agent.model_gates model/model.json
	python -m agent.model_gates model/model.mvm.json
	node tests/viewer_check.js viewer/bank-ontology.html

model:
	python -m agent.build_model

artefacts:
	python -m agent.export_artifacts

viewer:
	python -m agent.refresh_viewer

all: model artefacts viewer gate

clean:
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
