import logging
import requests
import os
from dotenv import load_dotenv
from typing import Any 
from .models import FredEndpoint

_ = load_dotenv()
API_KEY = os.getenv("API_KEY")

logger = logging.getLogger(__name__)

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

