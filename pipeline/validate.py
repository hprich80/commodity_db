from .models import SeriesMetaData, SeriesObservations
import logging
import datetime
from datetime import date

logger = logging.getLogger(__name__)

def check_nulls(obs: SeriesObservations, max_null_threshold: int = 2):
    if (null_count := sum(1 for v in obs.value[-3:] if v is None)) > max_null_threshold:
        logger.warning(f"{null_count} null rows for series {obs.series_id}. Threshold = {max_null_threshold}") 
    else:
        logger.info(f"Recent null rows ({null_count}) below threshold for series {obs.series_id}")

def check_performance(obs: SeriesObservations, max_perf_threshold: float = 1.5):
    count = 0
    for i in range(1, len(obs.value)):
        prev, cur = obs.value[i - 1], obs.value[i]
        if prev is None or cur is None or prev == 0:
            continue
        if (change := abs((cur - prev)/prev)) > max_perf_threshold:
            logger.warning(f"Performance of {change*100}% for series {obs.series_id} at {obs.date[i]}")
            count += 1
    if count > 0:
        logger.warning(f"{count} rows with unusual performance for series {obs.series_id}")
    else:
        logger.info(f"No rows with unusual performance for series {obs.series_id}")

def check_staleness(obs: SeriesObservations, metadata: SeriesMetaData, last_observation_date: date | None):
    freq: str = metadata.frequency
    freq_to_max_age = {"Daily":1, "Weekly":7, "Monthly":45}
    max_age = freq_to_max_age.get(freq)
    if max_age is None:
        logger.warning(f"No frequency metadata for series {metadata.series_id}")
        return
    if not last_observation_date:
        logger.warning(f"No last observation to check staleness for {metadata.series_id}")
        return
    if (datetime.date.today() - last_observation_date).days > max_age:
        logger.warning(f"Series {obs.series_id} is potentially stale. Last record  was {last_observation_date} (frequency: {metadata.frequency})")
    else:
        logger.info(f"Series {obs.series_id} (frequency: {metadata.frequency}) up to date")

def validate_series(obs: SeriesObservations, metadata: SeriesMetaData, last_observation_date: date | None, max_null_threshold: int = 2, max_perf_threshold: float = 1.5):
    check_nulls(obs, max_null_threshold)
    check_performance(obs, max_perf_threshold)
    check_staleness(obs, metadata, last_observation_date)


