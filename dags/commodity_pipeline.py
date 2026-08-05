import sys
sys.path.insert(0, '/opt/airflow/project')

import requests
from airflow import DAG  # pyright: ignore[reportMissingImports, reportUnknownVariableType]
from airflow.operators.python import PythonOperator  # pyright: ignore[reportMissingImports, reportUnknownVariableType]
from datetime import datetime
from pipeline.models import CommodityBasket, SeriesMetaData, SeriesObservations 
from pipeline.ingest import get_data
from pipeline.load import create_tables, insert_metadata, insert_observations
from db import get_connection
from pipeline.validate import validate_series 

def run_pipeline():
    conn = get_connection()

    create_tables(conn)

    with requests.Session() as session:
        for Commodity in CommodityBasket:
            series, obs = get_data(Commodity.value, session = session)
            metadata: SeriesMetaData = SeriesMetaData.from_FRED_response(Commodity.value, series)
            observations: SeriesObservations = SeriesObservations.from_FRED_response(Commodity.value, obs)
            validate_series(observations, metadata)
            insert_metadata(conn, metadata)
            insert_observations(conn, observations)

    conn.close()


with DAG(
    dag_id = "commodity_pipeline",
    schedule = "@daily",
    start_date = datetime(2024,1,1),
    catchup=False,
) as dag:

    pipeline_task = PythonOperator(
        task_id = "run_pipeline",
        python_callable = run_pipeline,
    )
