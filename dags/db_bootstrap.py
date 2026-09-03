import sys
sys.path.insert(0, '/opt/airflow/project')
from datetime import datetime
from airflow import DAG
from pipeline.load import create_tables
from airflow.operators.python import PythonOperator  # pyright: ignore[reportMissingImports, reportUnknownVariableType]

def pipeline_bootstrap():
    create_tables()

with DAG(
    start_date = datetime(2024,1,1),
    dag_id = 'db_bootstrap',
    schedule = None,
) as dag:
    pipeline_task = PythonOperator(  # pyright: ignore[reportUnknownVariableType]
        task_id = "pipeline_bootstrap",
        python_callable = pipeline_bootstrap,
    )
