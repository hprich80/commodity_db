from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host = 'localhost',
        dbname = 'fred_pipeline',
        user = 'postgres',
        password = 'password',
        port = 5432
    )

@app.route('/')
def index():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, date, value 
            FROM series_observations 
            WHERE id = 'POILBREUSDM' 
            ORDER BY date 
            DESC LIMIT 10"""
        )
        rows = cur.fetchall()
    conn.close()
    return render_template('index.html', rows=rows)

if __name__ == '__main__':
    app.run(debug=True)


