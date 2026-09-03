from collections import defaultdict
from datetime import date
from dashboard.queries import get_historical_prices, get_metadata
from pipeline.models import TradeData
from .models import Position
import numpy as np

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
            closed_quantity = net_quantity if closing_position else trade.quantity
            if inverse_trade:
                trade_realised_pnl = closed_quantity * (trade.price - avg_cost)
                trade_realised_pnl *= -1 if (net_quantity < 0 and not closing_position) else 1
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

def get_historical_prices_json_format():
    prices = get_historical_prices()
    json_prices: dict[str, dict[str, float]] = {
        series_id: {date.isoformat(date_key): value for date_key, value in observations.items()} 
        for series_id, observations in prices.items()
    }
    return json_prices

def calculate_pcnt_change(observations: dict[date, float], frequency: str): 
    limit = 31 if frequency == "Monthly" else 5
    last_date = list(observations.keys())[0]
    prev_date = list(observations.keys())[1]
    date_diff = np.busday_count(prev_date, last_date)
    today_diff = np.busday_count(last_date, date.today())
    last_price = observations[last_date]
    prev_price = observations[prev_date]
    if (date_diff > limit) or (today_diff > limit):
        pcnt_change = None
    else:
        pcnt_change = (last_price - prev_price)/prev_price
    return last_price, pcnt_change, last_date

def calculate_td(observations: dict[date, float], format: str): 
    td_format = {
        'mtd': date.today().month,
        'qtd': (date.today().month - 1)//3*3+1,
        'ytd': 1 
    }
    dates = list(observations.keys())
    last_date = dates[0] 
    first_date = date(date.today().year, td_format[format],1)
    # If last date is before or equal period start
    if last_date <= first_date:
        td = None
        return td
    # If last date is valid, but first_date doesn't return a price, walk backwards at least 5 days to find a valid price
    if not (first_price := observations.get(first_date)):
        candidate = first_date
        for i in range(1, len(dates)):
            candidate = dates[i]
            if candidate < first_date:
                break
        if np.busday_count(candidate, first_date) > 5:
            first_price = None
        else:
            first_price = observations.get(candidate)
    # If last date is after period start
    if first_price:
        last_price = observations[last_date]
        td = (last_price - first_price)/first_price
    else:
        td = None
    return td

def get_price_summary():
    prices = get_historical_prices()
    metadata = get_metadata()
    price_summary: dict[str, dict[str, float | date | None]] = {}
    for series_id, observations in prices.items():
        frequency: str = metadata[series_id]["frequency"]
        latest_price, pcnt_change, last_date = calculate_pcnt_change(observations, frequency)
        price_summary[series_id] = {
            'latest_price': latest_price,
            'pcnt_change': pcnt_change,
            'as_of': last_date,
            'mtd': calculate_td(observations, 'mtd'),
            'qtd': calculate_td(observations, 'qtd'),
            'ytd': calculate_td(observations, 'ytd')
        }
    return price_summary 
