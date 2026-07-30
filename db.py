import os
import psycopg2
from contextlib import contextmanager
from psycopg2.extensions import connection as PgConnection

def get_connection() -> PgConnection:
    db_url = os.getenv("DB_URL")
    return psycopg2.connect(db_url)

@contextmanager
def get_db_cursor():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
