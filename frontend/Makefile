.PHONY: install run build clean

install:
	@echo "Installing frontend dependencies..."
	npm install
	@echo "Done. Run 'make run' to start the frontend."

run:
	@if [ ! -d "node_modules" ]; then $(MAKE) install; fi
	@if [ ! -f ".env" ]; then cp .env.example .env && echo "Created .env from .env.example"; fi
	npm run dev

build:
	@if [ ! -d "node_modules" ]; then $(MAKE) install; fi
	npm run build

clean:
	rm -rf node_modules dist
