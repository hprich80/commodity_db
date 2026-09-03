import datetime
import pytest
from pipeline.models import SeriesObservations

def test_from_fred_response_parses_values():
    response = {"observations": [
        {"date": "2024-01-01", "value": "100.5"},
        {"date": "2024-01-02", "value": "101.0"},
    ]}
    result = SeriesObservations.from_FRED_response("TEST_SERIES", response)
    assert result.series_id == "TEST_SERIES"
    assert result.date == [datetime.date(2024, 1, 1), datetime.date(2024, 1, 2)]
    assert result.value == [100.5, 101.0]


def test_from_fred_response_dot_value_becomes_none():
    response = {"observations": [
        {"date": "2024-01-01", "value": "."},
        {"date": "2024-01-02", "value": "101.0"},
    ]}
    result = SeriesObservations.from_FRED_response("TEST_SERIES", response)
    assert result.value == [None, 101.0]


def test_from_fred_response_empty_observations():
    result = SeriesObservations.from_FRED_response("TEST_SERIES", {"observations": []})
    assert result.date == []
    assert result.value == []


def test_from_fred_response_missing_observations_key_raises():
    with pytest.raises(KeyError):
        SeriesObservations.from_FRED_response("TEST_SERIES", {})


def test_from_fred_response_missing_value_key_raises():
    response = {"observations": [{"date": "2024-01-01"}]}
    with pytest.raises(KeyError):
        SeriesObservations.from_FRED_response("TEST_SERIES", response)


def test_from_fred_response_unparseable_value_raises():
    response = {"observations": [{"date": "2024-01-01", "value": "not_a_number"}]}
    with pytest.raises(ValueError):
        SeriesObservations.from_FRED_response("TEST_SERIES", response)


def test_from_fred_response_malformed_date_raises():
    response = {"observations": [{"date": "not-a-date", "value": "100.0"}]}
    with pytest.raises(ValueError):
        SeriesObservations.from_FRED_response("TEST_SERIES", response)
