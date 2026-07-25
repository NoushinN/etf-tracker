.PHONY: install update demo dashboard test lint

install:
	python -m pip install -r requirements-dev.txt

update:
	python -m src.pipeline

demo:
	python -m src.pipeline --demo

dashboard:
	streamlit run dashboard/app.py

test:
	pytest -q

lint:
	ruff check .

