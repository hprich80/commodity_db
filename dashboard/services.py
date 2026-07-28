from collections import defaultdict
from datetime import date
from pipeline.models import TradeData
from .models import Position

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

