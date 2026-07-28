import datetime
from pipeline.models import TradeData
from dashboard.app import calculate_open_positions

def generate_test_data():
    trades = [
        # Simple long position
        TradeData('POILBREUSDM', datetime.date(2024, 1, 1), 'buy', 100.0, 10, datetime.date(2026, 1, 1)),
        # Add to long
        TradeData('POILBREUSDM', datetime.date(2024, 2, 1), 'buy', 110.0, 5, datetime.date(2026, 1, 1)),
        # Partial close
        TradeData('POILBREUSDM', datetime.date(2024, 3, 1), 'sell', 120.0, 5, datetime.date(2026, 1, 1)),
        # Second series
        TradeData('DCOILWTICO', datetime.date(2024, 1, 1), 'buy', 80.0, 20, datetime.date(2026, 1, 1)),
        # Full close and flip to short
        TradeData('DCOILWTICO', datetime.date(2024, 2, 1), 'sell', 90.0, 30, datetime.date(2026, 1, 1))
    ]

    latest_prices = {
        'POILBREUSDM': (datetime.date(2024, 6, 1), 115.0),
        'DCOILWTICO': (datetime.date(2024, 6, 1), 85.0),
    }

    return trades, latest_prices

def run():
    trades, latest_prices = generate_test_data()
    result = calculate_open_positions(latest_prices, trades)
    return result
