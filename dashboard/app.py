import os
from flask import Flask, redirect, render_template, request, url_for
from pipeline.models import TradeData
from .queries import get_historical_prices, get_latest_price, get_trades, insert_trade
from .services import calculate_open_positions 
from dotenv import load_dotenv

_ = load_dotenv(".env.local", override=True)
print("DB_URL:", os.getenv("DB_URL"))

app = Flask(__name__)

@app.route('/')
def index():
    historical_prices = get_historical_prices()
    latest_prices = get_latest_price()
    return render_template('index.html', historical_prices=historical_prices, latest_prices=latest_prices)

@app.route('/trades')
def trades():
    latest_prices = get_latest_price()
    trades = get_trades()
    return render_template('trades.html', latest_prices=latest_prices, trades=trades)

@app.route('/trades/new', methods=["GET", "POST"])
def new_trade():
    if request.method == "POST":
        trade = TradeData.from_form(
            series_id=request.form['series_id'],
            form=request.form
        )
        insert_trade(trade)
        return redirect(url_for('trades'))
    return render_template('new_trade.html')

@app.route('/portfolio')
def portfolio():
    latest_prices = get_latest_price()
    trades = get_trades()
    net_positions = calculate_open_positions(latest_prices, trades)
    return render_template('portfolio.html', net_positions=net_positions) 

if __name__ == '__main__':
    app.run(debug=True)

