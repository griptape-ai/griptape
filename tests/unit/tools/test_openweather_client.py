from unittest.mock import patch

import pytest

from griptape.artifacts import ErrorArtifact
from griptape.tools import OpenWeatherClient


@pytest.fixture()
def client():
    return OpenWeatherClient(api_key="YOUR_API_KEY")


class MockResponse:
    def __init__(self, json_data, status_code) -> None:
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mock_requests_get(*args, **kwargs):
    if args[0] == OpenWeatherClient.GEOCODING_URL:
        return MockResponse([{"lat": 40.7128, "lon": -74.0061}], 200)
    elif args[0] == OpenWeatherClient.BASE_URL:
        return MockResponse({"weather": "sunny"}, 200)
    return MockResponse(None, 404)


@patch("requests.get", side_effect=mock_requests_get)
def test_get_coordinates_by_location(mock_get, client):
    params = {"values": {"location": "New York, NY"}}
    result = client.get_coordinates_by_location(params)
    assert result.to_text() == "Coordinates for New York, NY: Latitude: 40.7128, Longitude: -74.0061"


@patch("requests.get", side_effect=mock_requests_get)
def test_get_current_weather_by_location(mock_get, client):
    params = {"values": {"location": "New York, NY"}}
    result = client.get_current_weather_by_location(params)
    assert result.to_text() == "{'weather': 'sunny'}"


@patch("requests.get", side_effect=mock_requests_get)
def test_get_hourly_forecast_by_location(mock_get, client):
    params = {"values": {"location": "New York, NY"}}
    result = client.get_hourly_forecast_by_location(params)
    assert result.to_text() == "{'weather': 'sunny'}"


@patch("requests.get", side_effect=mock_requests_get)
def test_get_daily_forecast_by_location(mock_get, client):
    params = {"values": {"location": "New York, NY"}}
    result = client.get_daily_forecast_by_location(params)
    assert result.to_text() == "{'weather': 'sunny'}"


@patch("requests.get", return_value=MockResponse(None, 401))
def test_invalid_api_key(mock_get, client):
    params = {"values": {"location": "New York, NY"}}
    result = client.get_coordinates_by_location(params)
    assert isinstance(result, ErrorArtifact)
    assert "Error fetching coordinates for location: New York, NY" in result.to_text()


@patch("requests.get", return_value=MockResponse(None, 404))
def test_invalid_location(mock_get, client):
    params = {"values": {"location": "InvalidCity, XX"}}
    result = client.get_coordinates_by_location(params)
    assert isinstance(result, ErrorArtifact)
    assert "Error fetching coordinates for location: InvalidCity, XX" in result.to_text()
