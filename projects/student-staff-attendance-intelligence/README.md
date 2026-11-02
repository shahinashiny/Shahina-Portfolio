# Student & Staff Attendance Intelligence Platform

An end-to-end data engineering portfolio implementation. It combines synthetic student/staff attendance, schedules, courses, faculty, and engagement records into curated analytical data, engineers rolling features, trains a risk classifier, tracks experiments, exposes REST endpoints, and prepares Power BI outputs.

**Data notice:** All records are generated with a fixed seed. No real student, employee, or institutional data is included. The label represents a simulated next-seven-day absence outcome. Metrics are synthetic-data demonstration results only.

## Architecture
Synthetic data generator → CSV landing zone → Airflow orchestration → validation/deduplication → Pandas or PySpark feature engineering → PostgreSQL and S3-compatible storage → Power BI. XGBoost/Scikit-learn trains a risk classifier, MLflow tracks experiments, and FastAPI serves summaries and scores.

## Implemented
- Reproducible synthetic student/staff attendance and engagement records.
- Validation, type conversion, invalid-row rejection, duplicate handling, and reject logs.
- Daily and rolling 7-record attendance/late/engagement features; daily and department summaries.
- Optional PySpark distributed transformation to Parquet.
- PostgreSQL publishing via SQLAlchemy and optional boto3 S3 upload; MinIO is provided locally.
- XGBoost classifier with Scikit-learn fallback, holdout evaluation, risk probabilities and low/medium/high bands.
- Optional MLflow tracking, FastAPI, Airflow DAG, Power BI/DAX guide, Docker Compose, tests and CI.

## Quick start
Python 3.11 recommended:
1. Create and activate a virtual environment.
2. Install: python -m pip install -r requirements.txt
3. Generate: python src/generate_data.py
4. Transform: python src/pipeline.py
5. Train/score: python src/train.py
6. Test: python -m pytest -q
7. API: uvicorn src.api:app --reload

Open http://127.0.0.1:8000/docs. The default generator creates 360 synthetic people over 90 calendar days (weekends skipped). Configure with --people, --days, and --seed.

## Outputs
- data/raw/attendance_events.csv — generated landing records
- data/processed/person_features.csv — validated and engineered rows
- data/processed/rejected_records.csv — invalid input rows
- data/processed/daily_summary.csv and department_summary.csv — reporting aggregates
- data/processed/latest_person_features.csv and risk_predictions.csv — latest person-level scores
- models/attendance_risk_model.joblib and models/metrics.json — model and holdout metrics

## Docker Compose
Run docker compose up --build -d. Then call POST http://localhost:8000/pipeline/run.
Services: API :8000, PostgreSQL :5432, MLflow :5000, MinIO console :9001 (local demo login minioadmin / minioadmin123). Demo credentials are not for production.

Optional Airflow: docker compose --profile orchestration up --build -d airflow. Open http://localhost:8080 and trigger student_staff_attendance_intelligence. Optional Spark: install Java and run python src/spark_job.py; it writes Parquet under data/processed/spark_features/.

## API
GET /health, GET /metrics, GET /daily-summary, GET /risk?limit=25&person_type=student, POST /pipeline/run.

## Power BI
Import daily_summary.csv, department_summary.csv, and risk_predictions.csv or connect to PostgreSQL. Use date, person_type, department, campus and risk_band as slicers. See powerbi/README.md for report pages and DAX.

## Responsible use
Synthetic IDs are not real identifiers. Never commit real student or employee data. The future-outcome field is used only to create the label and is removed from model inputs. Scores are human-review demonstration signals, never automated disciplinary, employment, academic or other high-stakes decisions. Replace all demo secrets with managed secrets and least-privilege IAM before cloud use.

## Production hardening
Before real-data use, add institution-approved secure ingestion, data contracts, idempotent backfills, partitioning, access control, privacy/retention review, pipeline/model drift monitoring, and formal model governance.