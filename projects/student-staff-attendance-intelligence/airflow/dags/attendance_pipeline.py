"""Daily Airflow orchestration for the synthetic attendance platform."""
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
PROJECT="/opt/project"
with DAG(dag_id="student_staff_attendance_intelligence",
    description="Generate, validate, transform and score synthetic attendance data",
    start_date=datetime(2026,1,1),schedule="@daily",catchup=False,max_active_runs=1,
    tags=["data-engineering","attendance","ml"]) as dag:
    generate=BashOperator(task_id="generate_synthetic_data",bash_command=f"cd {PROJECT} && python src/generate_data.py")
    transform=BashOperator(task_id="validate_transform_and_publish",bash_command=f"cd {PROJECT} && python src/pipeline.py")
    train=BashOperator(task_id="train_and_score_risk_model",bash_command=f"cd {PROJECT} && python src/train.py")
    generate >> transform >> train