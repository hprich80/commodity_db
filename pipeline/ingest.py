from dataclasses import dataclass
import datetime
import logging
import requests
import os
from dotenv import load_dotenv
from enum import Enum
from typing import Any 

_ = load_dotenv()
API_KEY = os.getenv("API_KEY")

logger = logging.getLogger(__name__)

class FredEndpoint(Enum):
    SERIES = "https://api.stlouisfed.org/fred/series"
    OBSERVATIONS = "https://api.stlouisfed.org/fred/series/observations"

class CommodityBasket(Enum):
    BRENT = "POILBREUSDM"
    WTI = "DCOILWTICO"
    NATURAL_GAS = "DHHNGSP"
    COPPER = "PCOPPUSDM"
    ALUMINIUM = "PALUMUSDM"
    WHEAT = "PWHEAMTUSDM"
    CORN = "PMAIZMTUSDM"
    DXY = "DTWEXBGS"
    TREASURY_10Y = "DGS10"

@dataclass
class Series:
    series_id: str

@dataclass
class SeriesMetaData(Series):
    realtime_start: str
    realtime_end: str
    title: str
    observation_start: str
    observation_end: str
    frequency: str
    frequency_short: str
    units: str
    units_short: str
    seasonal_adjustment: str
    seasonal_adjustment_short: str
    last_updated: str
    popularity: int
    notes: str

    @classmethod
    def from_FRED_response(cls, series_id: str, json: dict[str, Any]) -> 'SeriesMetaData':  # pyright: ignore[reportExplicitAny]

        logger.info(f"Constructing series metadata for {series_id}")

        if not (seriess_list := json.get('seriess')):
            logger.error(f"FRED response for {series_id} contains no series metadata. Response: {json}")
            raise KeyError(f"FRED response for {series_id} contains no series metadata.")

        seriess: dict[str, str] = seriess_list[0]  # pyright: ignore[reportAny]

        try:
            logger.info(f"Successfully parsed metadata for {series_id}")
            return cls(
                series_id = series_id,
                realtime_start = seriess['realtime_start'],
                realtime_end = seriess['realtime_end'],
                title = seriess['title'],
                observation_start = seriess['observation_start'],
                observation_end = seriess['observation_end'],
                frequency = seriess['frequency'],
                frequency_short = seriess['frequency_short'],
                units = seriess['units'],
                units_short = seriess['units_short'],
                seasonal_adjustment = seriess['seasonal_adjustment'],
                seasonal_adjustment_short = seriess['seasonal_adjustment_short'],
                last_updated = seriess['last_updated'],
                popularity = int(seriess['popularity']),
                notes = seriess['notes']
            )
        except KeyError as e:
            logger.error(f"Missing expected metadata for key {e} in FRED response for {series_id}")
            raise


@dataclass
class SeriesObservations(Series):
    date: list[datetime.date]
    value: list[float | None]

    @classmethod
    def from_FRED_response(cls, series_id: str, json: dict[str, Any]) -> 'SeriesObservations':  # pyright: ignore[reportExplicitAny]

        logger.info(f"Constructing series observations for {series_id}")

        if not (observations := json.get('observations')):
            logger.error(f"FRED response for {series_id} contains no series observations. Response: {json}")
            raise KeyError(f"FRED response for {series_id} contains no series observations.")

        datelist: list[datetime.date] = [] 
        valuelist: list[float | None] = []

        try:
            for obs in observations:  # pyright: ignore[reportAny]
                datelist.append(datetime.date.fromisoformat(obs['date']))  # pyright: ignore[reportAny]
                valuelist.append(None if obs['value'] == '.' else float(obs['value']))  # pyright: ignore[reportAny]
        except KeyError as e:
            logger.error(f"Failed to parse observations for {series_id}. Contains malformed key: {e}")
            raise
        except ValueError as e:
            logger.error(f"Failed to parse observations for {series_id}. Contains malformed value: {e}")
            raise

        logger.info(f"Successfully parsed {len(datelist)} observations for {series_id}. Rows with missing values: {valuelist.count(None)}")
        return cls(
            series_id = series_id,
            date = datelist,
            value = valuelist
        )

@dataclass
class TradeData:
    series_id: str
    trade_date: str
    direction: str
    price: float
    quantity: int

    @classmethod
    def from_form(cls, series_id: str, form: dict[str, str]) -> 'TradeData':
        logger.info(f"Parsing form for {series_id}")

        try:
            return cls(
                series_id = series_id,
                trade_date = form['trade_date'],
                direction = form['direction'],
                price = float(form['price']),
                quantity = int(form['quantity'])
            )

        except (ValueError, TypeError) as e:
            logger.error(f"Failed to parse form for {series_id}: {e}")
            raise


def get_data(series_id: str, session: requests.Session) -> tuple[dict[str,Any],dict[str,Any]]:  # pyright: ignore[reportExplicitAny]
    url_series = FredEndpoint.SERIES.value 
    url_obs = FredEndpoint.OBSERVATIONS.value
    PARAMS = {
        'api_key': API_KEY,
        'series_id': series_id,
        'file_type': 'json'
    }
    logger.info(f"Fetching data for series {series_id}")
    try:
        response_series = session.get(
            url_series,
            params=PARAMS
        )
        response_obs = session.get(
            url_obs,
            params=PARAMS
        )
        response_series.raise_for_status()
        response_obs.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Request failed for series {series_id=}: {e}")
        raise

    return response_series.json(), response_obs.json()

