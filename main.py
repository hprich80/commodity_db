from pipeline.ingest import get_data, SeriesMetaData, SeriesObservations, CommodityBasket  # pyright: ignore[reportImplicitRelativeImport]
from pipeline.load import get_connection, create_tables, insert_metadata, insert_observations  # pyright: ignore[reportImplicitRelativeImport]
import logging

logging.basicConfig(
    level=logging.INFO,
)

conn = get_connection()

create_tables(conn)

for Commodity in CommodityBasket:
    series, obs = get_data(Commodity.value)
    metadata: SeriesMetaData = SeriesMetaData.from_FRED_response(Commodity.value, series)
    observations: SeriesObservations = SeriesObservations.from_FRED_response(Commodity.value, obs)
    insert_metadata(conn, metadata)
    insert_observations(conn, observations)

conn.close()
