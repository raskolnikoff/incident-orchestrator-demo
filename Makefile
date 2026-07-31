.PHONY: validate test diagrams generate-data summary linkedin-assets clean help

PYTHON ?= python3

help:
	@echo "Targets:"
	@echo "  make generate-data    Regenerate dataset/*.jsonl and *.csv (fixed seed=42)"
	@echo "  make validate         Run dataset, example, and LinkedIn-asset validators"
	@echo "  make test             Run the tests/ unittest suite"
	@echo "  make diagrams         Render diagrams/source/*.puml to diagrams/rendered/"
	@echo "  make linkedin-assets  Export assets/linkedin/source/*.svg to rendered/"
	@echo "  make summary          Print a compact dataset statistical summary"
	@echo "  make clean            Remove rendered diagrams"

generate-data:
	$(PYTHON) scripts/generate_dataset.py

validate:
	$(PYTHON) scripts/validate_dataset.py
	$(PYTHON) scripts/validate_examples.py
	$(PYTHON) scripts/validate_linkedin_assets.py

test:
	$(PYTHON) -m unittest discover -s tests -v

diagrams:
	bash scripts/render_diagrams.sh

linkedin-assets:
	$(PYTHON) scripts/export_linkedin_assets.py

summary:
	$(PYTHON) scripts/generate_dataset_summary.py

clean:
	rm -f diagrams/rendered/*.svg diagrams/rendered/*.png
