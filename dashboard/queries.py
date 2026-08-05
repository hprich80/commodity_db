from collections import defaultdict
from datetime import date
from db import get_db_cursor
from pipeline.models import TradeData

def get_latest_price():
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT ON (series_id)
            series_id, date, value
            FROM series_observations
            WHERE value IS NOT NULL
            ORDER BY series_id, date DESC
            """
        )
        rows: list[tuple[str, date, float]] = cur.fetchall()
        latest_prices: dict[str, tuple[date, float]] = {
            series_id: (date, value) 
            for series_id, date, value in rows
        }
    return latest_prices

def get_historical_prices(): 
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT series_id, date, value 
            FROM series_observations 
            ORDER BY series_id, date DESC 
            """
        )
        rows: list[tuple[str, date, float]] = cur.fetchall()
        prices: dict[str, dict[date, float]] = defaultdict(dict)
        for series_id, price_date, value in rows:
            if series_id not in prices:
                prices[series_id] = {}
            prices[series_id][price_date] = value

        return prices

def get_trades() -> list[TradeData]:
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT series_id, trade_date, direction, price, quantity, created_at
            FROM trade_data
            """
        )
        result: list[tuple[str, date, str, float, int, date]] = cur.fetchall()
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


def insert_trade(trade: TradeData):
    with get_db_cursor() as cur:
        row = (trade.series_id, trade.direction, trade.trade_date, trade.price, trade.quantity)
        cur.execute("""
                    INSERT INTO trade_data (series_id, direction, trade_date, price, quantity, created_at)
                    VALUES (%s, %s, %s, %s, %s, NOW());
                    """, row
                    )

def get_metadata() -> dict[str, dict[str, str]]:
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT series_id, title, frequency, units, seasonal_adjustment, last_updated, popularity, notes 
            FROM series_metadata"""
        )
        result: list[tuple[str, str, str, str, str, str, str, str]] = cur.fetchall()
        metadata = {
            series_id: {
                "title": title,
                "frequency": frequency,
                "units": units,
                "seasonal_adjustment": seasonal_adjustment,
                "last_updated": last_updated,
                "popularity": popularity,
                "notes": notes,
            }
            for (series_id, title, frequency, units, seasonal_adjustment, last_updated, popularity, notes) in result
        }
        return metadata

