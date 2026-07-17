from flask import Flask, render_template
import psycopg2
from psycopg2.extensions import cursor
from pipeline.ingest import TradeData

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host = 'localhost',
        dbname = 'fred_pipeline',
        user = 'postgres',
        password = 'password',
        port = 5432
    )

def calculate_holdings():
    return None

def get_latest_price(cur: cursor) :
    cur.execute(
        """
        SELECT DISTINCT ON (series_id)
        series_id, date, value
        FROM series_observations
        WHERE value IS NOT NULL
        ORDER BY series_id, date DESC
        """
    )
    rows = cur.fetchall()
    latest_prices = {
        series_id: (date, value) 
        for series_id, date, value in rows
    }
    return latest_prices


def get_historical_prices(cur: cursor):
    cur.execute(
        """
        SELECT series_id, date, value 
        FROM series_observations 
        ORDER BY series_id, date DESC 
        """
    )
    rows = cur.fetchall()
    prices = {}
    for series_id, date, value in rows:
        if series_id not in prices:
            prices[series_id] = {}
        prices[series_id][date] = value

    return prices

def get_trades(cur: cursor) -> list[TradeData]:
    cur.execute(
        """
        SELECT series_id, trade_date, direction, price, quantity
        FROM trade_data
        """
    )
    result = cur.fetchall()
    trades = [
        TradeData(
            series_id,
            trade_date,
            direction,
            price,
            quantity
        )
        for series_id, trade_date, direction, price, quantity in result
    ]
    return trades

@app.route('/')
def index():
    conn = get_connection()
    with conn.cursor() as cur:
        latest_prices = get_latest_price(cur)
        historical_prices = get_historical_prices(cur)
        trades = get_trades(cur)

    conn.close()
    return render_template('index.html', historical_prices=historical_prices, latest_prices=latest_prices, trades=trades)

if __name__ == '__main__':
    app.run(debug=True)

