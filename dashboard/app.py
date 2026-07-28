from collections import defaultdict
from dataclasses import dataclass
from datetime import date
import datetime
from flask import Flask, redirect, render_template, request, url_for
import psycopg2
from psycopg2.extensions import cursor
from pipeline.ingest import TradeData
from pipeline.load import insert_trade

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host = 'localhost',
        dbname = 'fred_pipeline',
        user = 'postgres',
        password = 'password',
        port = 5432
    )

def get_latest_price(cur: cursor):
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
    latest_prices: dict[str, tuple[datetime.date, float]] = {
        series_id: (date, value) 
        for series_id, date, value in rows
    }
    return latest_prices


def get_historical_prices(cur: cursor) -> dict[str, dict[str, str]]:
    cur.execute(
        """
        SELECT series_id, date, value 
        FROM series_observations 
        ORDER BY series_id, date DESC 
        """
    )
    rows: list[tuple[str, str, str]] = cur.fetchall()
    prices = {}
    for series_id, date, value in rows:
        if series_id not in prices:
            prices[series_id] = {}
        prices[series_id][date] = value

    return prices

def get_trades(cur: cursor) -> list[TradeData]:
    cur.execute(
        """
        SELECT series_id, trade_date, direction, price, quantity, created_at
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
            quantity,
            created_at
        )
        for series_id, trade_date, direction, price, quantity, created_at in result
    ]
    return trades

@app.route('/')
def index():
    conn = get_connection()
    with conn.cursor() as cur:
        historical_prices = get_historical_prices(cur)

    conn.close()
    return render_template('index.html', historical_prices=historical_prices)

@app.route('/trades')
def trades():
    conn = get_connection()
    with conn.cursor() as cur:
        latest_prices = get_latest_price(cur)
        trades = get_trades(cur)
    conn.close()
    return render_template('trades.html', latest_prices=latest_prices, trades=trades)

@app.route('/trades/new', methods=["GET", "POST"])
def new_trade():
    if request.method == "POST":
        trade = TradeData.from_form(
            series_id=request.form['series_id'],
            form=request.form
        )
        conn = get_connection()
        insert_trade(conn, trade)
        conn.close()
        return redirect(url_for('trades'))
    return render_template('new_trade.html')

@dataclass
class Position:
    series_id: str
    net_quantity: int
    avg_cost: float
    current_price: float
    unrealised_pnl: float
    realised_pnl: float

def calculate_open_positions(latest_prices: dict[str, tuple[date, float]], trades: list[TradeData]):
    trades_by_series: defaultdict[str, list[TradeData]]  = defaultdict(list)
    for trade in trades:
        trades_by_series[trade.series_id].append(trade)
    net_positions: list[Position] = [] 
    for series in trades_by_series:

        trades_by_series[series].sort(key=lambda t: t.trade_date)
        net_quantity: int = 0
        avg_cost: float = 0
        realised_pnl: float = 0

        for trade in trades_by_series[series]:
            trade_quantity = trade.quantity if trade.direction == 'buy' else -trade.quantity
            closing_position = True if (trade_quantity*net_quantity) < 0 and (abs(trade_quantity) > abs(net_quantity)) else False
            inverse_trade = True if trade_quantity*net_quantity < 0 else False
            closed_quantity = net_quantity if closing_position else trade_quantity
            if inverse_trade:
                trade_realised_pnl = closed_quantity * (trade.price - avg_cost)
                trade_realised_pnl *= -1 if net_quantity < 0 else 1
                realised_pnl += trade_realised_pnl
                if closing_position:
                    avg_cost = trade.price
            else:
                avg_cost = (avg_cost*net_quantity + trade.price*trade_quantity) / (net_quantity + trade_quantity)
            net_quantity += trade_quantity

        current_price = latest_prices[series][1]
        unrealised_pnl = net_quantity * (current_price - avg_cost)
        position = Position(series, net_quantity, avg_cost, current_price, unrealised_pnl, realised_pnl) 
        net_positions.append(position)

    return net_positions

@app.route('/portfolio')
def portfolio():
    conn = get_connection()
    with conn.cursor() as cur:
        latest_prices = get_latest_price(cur)
        trades = get_trades(cur)
    conn.close()
    net_positions = calculate_open_positions(latest_prices, trades)
    return render_template('portfolio.html', net_positions=net_positions) 

if __name__ == '__main__':
    app.run(debug=True)

