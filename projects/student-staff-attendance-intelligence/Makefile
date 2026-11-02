.PHONY: install data pipeline train test api
install:
	python -m pip install -r requirements.txt
data:
	python src/generate_data.py
pipeline: data
	python src/pipeline.py
train: pipeline
	python src/train.py
test:
	python -m pytest -q
api:
	uvicorn src.api:app --reload