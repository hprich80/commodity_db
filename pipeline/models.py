
from dataclasses import dataclass
import datetime
import logging
from enum import Enum
from typing import Any 

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

@dataclass()
class Series:
    series_id: str

@dataclass
class SeriesMetaData(Series):
    title: str
    frequency: str
    units: str
    seasonal_adjustment: str
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
                title = seriess['title'],
                frequency = seriess['frequency'],
                units = seriess['units'],
                seasonal_adjustment = seriess['seasonal_adjustment'],
                last_updated = seriess['last_updated'],
                popularity = int(seriess['popularity']),
                notes = seriess['notes']
            )
        except KeyError as e:
            logger.error(f"Missing expected metadata for key {e} in FRED response for {series_id}")
            raise

    @classmethod
    def from_db_query(cls, db_response: tuple[Any, ...]) -> 'SeriesMetaData':
        try:
            return cls(*db_response)
        except TypeError as e:
            series_id: str = db_response[0] if db_response else "<empty_row>"
            logger.error(f"Malformed DB row for {series_id}: {e}")
            raise

@dataclass
class SeriesObservations(Series):
    date: list[datetime.date]
    value: list[float | None]

    @classmethod
    def from_FRED_response(cls, series_id: str, json: dict[str, Any]) -> 'SeriesObservations':  # pyright: ignore[reportExplicitAny]

        logger.info(f"Constructing series observations for {series_id}")

        if (observations := json.get('observations')) is None:
            logger.error(f"FRED response for {series_id} contains no series observations. Response: {json}")
            raise KeyError(f"FRED response for {series_id} contains no series observations.")
        if not observations:
            logger.info(f"No new observations for {series_id}")

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
    trade_date: datetime.date
    direction: str
    price: float
    quantity: int
    created_at: datetime.date | None

    @classmethod
    def from_form(cls, series_id: str, form: dict[str, str]) -> 'TradeData':
        logger.info(f"Parsing form for {series_id}")

        try:
            return cls(
                series_id = series_id,
                trade_date = datetime.date.fromisoformat(form['trade_date']),
                direction = form['direction'],
                price = float(form['price']),
                quantity = int(form['quantity']),
                created_at = None 
            ) 
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to parse form for {series_id}: {e}")
            raise

