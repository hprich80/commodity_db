from .models import SeriesMetaData, SeriesObservations 
import logging
from psycopg2.extensions import connection as PgConnection
from db import get_db_cursor
logger = logging.getLogger(__name__)


def create_tables():
    with get_db_cursor() as cur:
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS series_metadata(
                        series_id VARCHAR PRIMARY KEY,
                        title TEXT,
                        frequency TEXT,
                        units TEXT,
                        seasonal_adjustment TEXT,
                        last_updated TEXT,
                        popularity INT,
                        notes TEXT,
                        fetched_at TIMESTAMP DEFAULT NOW()
                    );
                """)
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS series_observations(
                        series_id VARCHAR REFERENCES series_metadata(series_id),
                        date DATE,
                        value NUMERIC,
                        fetched_at TIMESTAMP DEFAULT NOW(),
                        PRIMARY KEY(series_id, date)
                    );
                """)
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS trade_data(
                        trade_id SERIAL PRIMARY KEY,
                        series_id VARCHAR REFERENCES series_metadata(series_id),
                        trade_date DATE,
                        direction TEXT,
                        price NUMERIC,
                        quantity INT,
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)

def insert_metadata(metadata: SeriesMetaData):
    with get_db_cursor() as cur:
        cur.execute("""
                    INSERT INTO series_metadata (series_id, title, frequency, units, seasonal_adjustment, last_updated, popularity, notes, fetched_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (series_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        frequency = EXCLUDED.frequency,
                        units = EXCLUDED.units,
                        seasonal_adjustment = EXCLUDED.seasonal_adjustment,
                        last_updated = EXCLUDED.last_updated,
                        popularity = EXCLUDED.popularity,
                        notes = EXCLUDED.notes,
                        fetched_at = EXCLUDED.fetched_at
                    WHERE (series_metadata.title, series_metadata.frequency, series_metadata.units, series_metadata.seasonal_adjustment, series_metadata.last_updated, series_metadata.popularity, series_metadata.notes)
                    IS DISTINCT FROM 
                        (EXCLUDED.title, EXCLUDED.frequency, EXCLUDED.units, EXCLUDED.seasonal_adjustment, EXCLUDED.last_updated, EXCLUDED.popularity, EXCLUDED.notes)
                    """, (metadata.series_id, metadata.title, metadata.frequency, metadata.units, metadata.seasonal_adjustment, metadata.last_updated, metadata.popularity, metadata.notes)
                    )
        if cur.rowcount > 0:
            logger.info(f"Upserted metadata for {metadata.series_id}")
        else:
            logger.info(f"No metadata changed for {metadata.series_id}")

def insert_observations(observations: SeriesObservations):
    with get_db_cursor() as cur:
        rows= zip(observations.date, observations.value)
        cur.executemany("""
                    INSERT INTO series_observations (series_id, date, value, fetched_at)
                    VALUES (%s , %s, %s, NOW())
                    ON CONFLICT (series_id, date) DO UPDATE SET
                        value = EXCLUDED.value,
                        fetched_at = EXCLUDED.fetched_at
                    WHERE series_observations.value IS DISTINCT FROM EXCLUDED.value;
                    """, [(observations.series_id, date, value) for date, value in rows]
                    )
        if cur.rowcount > 0:
            logger.info(f"Upserted {cur.rowcount} rows for {observations.series_id}")
        else:
            logger.info(f"No rows upserted for {observations.series_id}")

