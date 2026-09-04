import sys
sys.path.insert(0, '/opt/airflow/project')
from airflow.sdk import dag, task
import requests
from datetime import datetime, timedelta
from pipeline.models import CommodityBasket, SeriesMetaData, SeriesObservations 
from pipeline.ingest import get_data
from pipeline.load import get_latest_observation_date, insert_metadata, insert_observations
from pipeline.validate import validate_series 

@dag(
    dag_id = "commodity_pipeline",
    schedule = "@daily",
    start_date = datetime(2024,1,1),
    catchup=False,
)
def commodity_pipeline():
    @task(
        retries = 3,
        retry_delay=timedelta(seconds=5),
        execution_timeout=timedelta(minutes=10),
        retry_exponential_backoff=True
    )
    def process_series(commodity: str):
        last_observation = get_latest_observation_date(commodity)
        start_date = last_observation + timedelta(days=1) if last_observation else None

        with requests.Session() as session:
            series, obs = get_data(commodity, session = session, observation_start=start_date)
            metadata: SeriesMetaData = SeriesMetaData.from_FRED_response(commodity, series)
            observations: SeriesObservations = SeriesObservations.from_FRED_response(commodity, obs)
            validate_series(observations, metadata, last_observation)
            insert_metadata(metadata)
            insert_observations(observations)

    process_series.expand(commodity=[c.value for c in CommodityBasket])

_ = commodity_pipeline()
