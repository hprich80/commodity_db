import psycopg2

def get_connection():
    return psycopg2.connect(
        host = 'localhost',
        dbname = 'fred_pipeline',
        user = 'postgres',
        password = 'password',
        port = 5432
    )

