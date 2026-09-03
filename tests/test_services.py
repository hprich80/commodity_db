from dashboard.models import Position
from dashboard.services import calculate_open_positions

def test_long_partial_close(latest_prices, long_position_partial_close):
    trades = long_position_partial_close
    result = calculate_open_positions(latest_prices, trades)
    assert result == [
        Position('POILBREUSDM', 5, 100.0, latest_prices['POILBREUSDM'][1], 75.0, 50.0),
        Position('DCOILWTICO', 5, 100.0, latest_prices['DCOILWTICO'][1], 75.0, 50.0),
    ] 

def test_short_partial_close(latest_prices, short_position_partial_close):
    trades = short_position_partial_close
    result = calculate_open_positions(latest_prices, trades)
    assert result == [
        Position('POILBREUSDM', -5, 110.0, latest_prices['POILBREUSDM'][1], -25.0, 50.0),
        Position('DCOILWTICO', -5, 110.0, latest_prices['DCOILWTICO'][1], -25.0, 50.0),
    ] 

def test_long_full_close(latest_prices, long_close_to_flat):
    result = calculate_open_positions(latest_prices, long_close_to_flat)
    assert result == [
        Position('POILBREUSDM', 0, 100.0, latest_prices['POILBREUSDM'][1], 0.0, 100.0),
        Position('DCOILWTICO', 0, 100.0, latest_prices['DCOILWTICO'][1], 0.0, 100.0),
    ]

def test_short_full_close(latest_prices, short_close_to_flat):
    result = calculate_open_positions(latest_prices, short_close_to_flat)
    assert result == [
        Position('POILBREUSDM', 0, 100.0, latest_prices['POILBREUSDM'][1], 0.0, -100.0),
        Position('DCOILWTICO', 0, 100.0, latest_prices['DCOILWTICO'][1], 0.0, -100.0),
    ]

def test_flip_long_to_short(latest_prices, flip_long_to_short):
    result = calculate_open_positions(latest_prices, flip_long_to_short)
    assert result == [
        Position('POILBREUSDM', -5, 110.0, latest_prices['POILBREUSDM'][1], -25.0, 100.0),
        Position('DCOILWTICO', -5, 110.0, latest_prices['DCOILWTICO'][1], -25.0, 100.0),
    ]

def test_flip_short_to_long(latest_prices, flip_short_to_long):
    result = calculate_open_positions(latest_prices, flip_short_to_long)
    assert result == [
        Position('POILBREUSDM', 5, 100.0, latest_prices['POILBREUSDM'][1], 75.0, 100.0),
        Position('DCOILWTICO', 5, 100.0, latest_prices['DCOILWTICO'][1], 75.0, 100.0),
    ]

def test_addition_to_long_changes_avg_cost(latest_prices, addition_to_long):
    result = calculate_open_positions(latest_prices, addition_to_long)
    assert result == [
        Position('POILBREUSDM', 20, 105.0, latest_prices['POILBREUSDM'][1], 200.0, 0.0),
        Position('DCOILWTICO', 20, 105.0, latest_prices['DCOILWTICO'][1], 200.0, 0.0),
    ]

def test_addition_to_short_changes_avg_cost(latest_prices, addition_to_short):
    result = calculate_open_positions(latest_prices, addition_to_short)
    assert result == [
        Position('POILBREUSDM', -20, 105.0, latest_prices['POILBREUSDM'][1], -200.0, 0.0),
        Position('DCOILWTICO', -20, 105.0, latest_prices['DCOILWTICO'][1], -200.0, 0.0),
    ]

def test_reopen_after_flat(latest_prices, reopen_after_flat):
    result = calculate_open_positions(latest_prices, reopen_after_flat)
    assert result == [
        Position('POILBREUSDM', 5, 120.0, latest_prices['POILBREUSDM'][1], -25.0, 100.0),
        Position('DCOILWTICO', 5, 120.0, latest_prices['DCOILWTICO'][1], -25.0, 100.0),
    ]

