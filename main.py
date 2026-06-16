from pipeline.ingest import get_data, SeriesMetaData, SeriesObservations, CommodityBasket 
from pipeline.load import get_connection, create_tables, insert_metadata, insert_observations 
from pipeline.validate import validate_series
import logging
import requests

logging.basicConfig(
    level=logging.INFO,
)

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

