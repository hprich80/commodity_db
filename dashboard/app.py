from flask import Flask, redirect, render_template, request, url_for
from pipeline.models import TradeData
from pipeline.load import insert_trade
from .db import get_connection
from .queries import get_historical_prices, get_latest_price, get_trades
from .services import calculate_open_positions 

app = Flask(__name__)


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

