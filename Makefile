#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = fplume_montecarlo
PYTHON_VERSION = 3.9.5
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python dependencies
.PHONY: requirements
requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt
	



## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete


## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	ruff format --check
	ruff check

## Format source code with ruff
.PHONY: format
format:
	ruff check --fix
	ruff format





## Set up Python interpreter environment
.PHONY: create_environment
create_environment:
	@bash -c "if [ ! -z `which virtualenvwrapper.sh` ]; then source `which virtualenvwrapper.sh`; mkvirtualenv $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER); else mkvirtualenv.bat $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER); fi"
	@echo ">>> New virtualenv created. Activate with:\nworkon $(PROJECT_NAME)"
	



#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


## Make dataset
.PHONY: data
data: requirements
	$(PYTHON_INTERPRETER) fplume_montecarlo/dataset.py


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)

## Run the full pipeline for all codes
.PHONY: run-all
run-all:
	@bash -c "source venv/bin/activate && cd src && \
	python -m fplume_montecarlo.download_era5 --all && \
	python -m fplume_montecarlo.create_met_file --all && \
	python -m fplume_montecarlo.prepare_input_files --all && \
	python -m fplume_montecarlo.run_montecarlo --all && \
	python -m fplume_montecarlo.plot_montecarlo && \
	python -m fplume_montecarlo.qqplot_montecarlo"

## Run the pipeline for a specific code: make run-code CODE=123
.PHONY: run-code
run-code:
ifndef CODE
	$(error CODE is not set. Usage: make run-code CODE=123)
endif
	@bash -c "source venv/bin/activate && cd src && \
	python -m fplume_montecarlo.download_era5 --code $(CODE) && \
	python -m fplume_montecarlo.create_met_file --code $(CODE) && \
	python -m fplume_montecarlo.prepare_input_files --code $(CODE) && \
	python -m fplume_montecarlo.run_montecarlo --code $(CODE) && \
	python -m fplume_montecarlo.plot_montecarlo && \
	python -m fplume_montecarlo.qqplot_montecarlo"
