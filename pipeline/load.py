import psycopg2
from psycopg2.extensions import connection as PgConnection
from .ingest import SeriesMetaData, SeriesObservations
import logging

logger = logging.getLogger(__name__)

def get_connection() -> PgConnection:
    return psycopg2.connect(
        host = 'localhost',
        dbname = 'fred_pipeline',
        user = 'postgres',
        password = 'password',
        port = 5432
    )

def create_tables(conn: PgConnection):
    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS series_metadata(
                        id VARCHAR PRIMARY KEY,
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
                        id VARCHAR REFERENCES series_metadata(id),
                        date DATE,
                        value NUMERIC,
                        fetched_at TIMESTAMP DEFAULT NOW(),
                        PRIMARY KEY(id, date)
                    );
                """)
        conn.commit()

def insert_metadata(conn: PgConnection, metadata: SeriesMetaData):
    with conn.cursor() as cur:
        cur.execute("""
                    INSERT INTO series_metadata (id, title, frequency, units, seasonal_adjustment, last_updated, popularity, notes, fetched_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (id) DO UPDATE SET
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
                    """, (metadata.id, metadata.title, metadata.frequency, metadata.units, metadata.seasonal_adjustment, metadata.last_updated, metadata.popularity, metadata.notes)
                    )

        if cur.rowcount > 0:
            logger.info(f"Upserted metadata for {metadata.id}")
        else:
            logger.info(f"No metadata changed for {metadata.id}")

        conn.commit()

def insert_observations(conn: PgConnection, observations: SeriesObservations):
    with conn.cursor() as cur:
        rows= zip(observations.date, observations.value)
        cur.executemany("""
                    INSERT INTO series_observations (id, date, value, fetched_at)
                    VALUES (%s , %s, %s, NOW())
                    ON CONFLICT (id, date) DO UPDATE SET
                        value = EXCLUDED.value,
                        fetched_at = EXCLUDED.fetched_at
                    WHERE series_observations.value IS DISTINCT FROM EXCLUDED.value;
                    """, [(observations.id, date, value) for date, value in rows]
                    )

        if cur.rowcount > 0:
            logger.info(f"Upserted {cur.rowcount} rows for {observations.id}")
        else:
            logger.info(f"No rows upserted for {observations.id}")

        conn.commit()

