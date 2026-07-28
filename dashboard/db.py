from contextlib import contextmanager

import psycopg2

def get_connection():
    return psycopg2.connect(
        host = 'localhost',
        dbname = 'fred_pipeline',
        user = 'postgres',
        password = 'password',
        port = 5432
    )

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
