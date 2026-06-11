.PHONY: install run mcp clean

VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

ifeq ($(OS),Windows_NT)
	PYTHON=$(VENV)/Scripts/python
	PIP=$(VENV)/Scripts/pip
endif

install:
	@echo "Creating virtual environment..."
	python -m venv $(VENV)
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Done. Run 'make run' to start the backend."

run:
	@if [ ! -d "$(VENV)" ]; then $(MAKE) install; fi
	@if [ ! -f ".env" ]; then cp .env.example .env && echo "Created .env from .env.example — fill in your GEMINI_API_KEY"; fi
	@mkdir -p data
	$(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

mcp:
	@if [ ! -d "$(VENV)" ]; then $(MAKE) install; fi
	$(PYTHON) mcp_server.py

clean:
	rm -rf $(VENV) __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
