.DEFAULT_GOAL := run

run:
	python3 src/main.py

clean:
	rm -r src/__pycache__

.PHONY: run clean