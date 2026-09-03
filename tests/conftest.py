import datetime
from pipeline.models import TradeData
import pytest

@pytest.fixture
def latest_prices():
    return {
        'POILBREUSDM': (datetime.date(2024, 6, 1), 115.0),
        'DCOILWTICO': (datetime.date(2024, 6, 1), 115.0)
    }

@pytest.fixture
def long_position_partial_close():
    return [
        TradeData('POILBREUSDM', datetime.date(2024, 1, 1), 'buy', 100.0, 10, datetime.date(2026, 1, 1)),
        TradeData('POILBREUSDM', datetime.date(2024, 3, 1), 'sell', 110.0, 5, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 1, 1), 'buy', 100.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 3, 1), 'sell', 110.0, 5, datetime.date(2026, 1, 1))
    ]

@pytest.fixture
def short_position_partial_close():
    return [
        TradeData('POILBREUSDM', datetime.date(2024, 1, 1), 'sell', 110.0, 10, datetime.date(2026, 1, 1)),
        TradeData('POILBREUSDM', datetime.date(2024, 3, 1), 'buy', 100.0, 5, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 1, 1), 'sell', 110.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 3, 1), 'buy', 100.0, 5, datetime.date(2026, 1, 1))
    ]

@pytest.fixture
def long_close_to_flat():
    return [
        TradeData('POILBREUSDM', datetime.date(2024, 1, 1), 'buy', 100.0, 10, datetime.date(2026, 1, 1)),
        TradeData('POILBREUSDM', datetime.date(2024, 3, 1), 'sell', 110.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 1, 1), 'buy', 100.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 3, 1), 'sell', 110.0, 10, datetime.date(2026, 1, 1)),
    ]

@pytest.fixture
def short_close_to_flat():
    return [
        TradeData('POILBREUSDM', datetime.date(2024, 1, 1), 'sell', 100.0, 10, datetime.date(2026, 1, 1)),
        TradeData('POILBREUSDM', datetime.date(2024, 3, 1), 'buy', 110.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 1, 1), 'sell', 100.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 3, 1), 'buy', 110.0, 10, datetime.date(2026, 1, 1)),
    ]


@pytest.fixture
def flip_long_to_short():
    return [
        TradeData('POILBREUSDM', datetime.date(2024, 1, 1), 'buy', 100.0, 10, datetime.date(2026, 1, 1)),
        TradeData('POILBREUSDM', datetime.date(2024, 3, 1), 'sell', 110.0, 15, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 1, 1), 'buy', 100.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 3, 1), 'sell', 110.0, 15, datetime.date(2026, 1, 1)),
    ]

@pytest.fixture
def flip_short_to_long():
    return [
        TradeData('POILBREUSDM', datetime.date(2024, 1, 1), 'sell', 110.0, 10, datetime.date(2026, 1, 1)),
        TradeData('POILBREUSDM', datetime.date(2024, 3, 1), 'buy', 100.0, 15, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 1, 1), 'sell', 110.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 3, 1), 'buy', 100.0, 15, datetime.date(2026, 1, 1)),
    ]

@pytest.fixture
def addition_to_long():
    return [
        TradeData('POILBREUSDM', datetime.date(2024, 1, 1), 'buy', 100.0, 10, datetime.date(2026, 1, 1)),
        TradeData('POILBREUSDM', datetime.date(2024, 2, 1), 'buy', 110.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 1, 1), 'buy', 100.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 2, 1), 'buy', 110.0, 10, datetime.date(2026, 1, 1)),
    ]

@pytest.fixture
def addition_to_short():
    return [
        TradeData('POILBREUSDM', datetime.date(2024, 1, 1), 'sell', 110.0, 10, datetime.date(2026, 1, 1)),
        TradeData('POILBREUSDM', datetime.date(2024, 2, 1), 'sell', 100.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 1, 1), 'sell', 110.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 2, 1), 'sell', 100.0, 10, datetime.date(2026, 1, 1)),
    ]

@pytest.fixture
def reopen_after_flat():
    return [
        TradeData('POILBREUSDM', datetime.date(2024, 1, 1), 'buy', 100.0, 10, datetime.date(2026, 1, 1)),
        TradeData('POILBREUSDM', datetime.date(2024, 2, 1), 'sell', 110.0, 10, datetime.date(2026, 1, 1)),
        TradeData('POILBREUSDM', datetime.date(2024, 3, 1), 'buy', 120.0, 5, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 1, 1), 'buy', 100.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 2, 1), 'sell', 110.0, 10, datetime.date(2026, 1, 1)),
        TradeData('DCOILWTICO', datetime.date(2024, 3, 1), 'buy', 120.0, 5, datetime.date(2026, 1, 1)),
    ]

