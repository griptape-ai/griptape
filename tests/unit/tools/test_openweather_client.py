import pytest
from griptape.artifacts import TextArtifact, ErrorArtifact
from griptape.tools import OpenWeatherClient

@pytest.fixture
def weather_client():
    api_key = "YOUR_API_KEY"
    return OpenWeatherClient(api_key=api_key)

def test_get_weather_by_city(weather_client, mocker):
    mock_response_data = {
        "weather": [{
            "description": "clear sky"
        }],
        "main": {
            "temp": 67.73
        }
    }
    mock_get = mocker.patch('griptape.tools.openweather_client.tool.requests.get')
    mock_get.return_value.json.return_value = mock_response_data
    mock_get.return_value.status_code = 200

    city_name = "London"
    response_artifact = weather_client._get_weather_by_city({"values": {"city_name": city_name}})

    assert isinstance(response_artifact, TextArtifact)

    response_data = eval(response_artifact.to_text())

    assert response_data["weather"][0]["description"] == "clear sky"
    assert response_data["main"]["temp"] == 67.73

def test_get_weather_by_city_error(weather_client, mocker):
    mock_get = mocker.patch('griptape.tools.openweather_client.tool.requests.get')
    mock_get.return_value.status_code = 404

    city_name = "NonExistentCity"
    response_artifact = weather_client._get_weather_by_city({"values": {"city_name": city_name}})

    assert isinstance(response_artifact, ErrorArtifact)
    assert "Error fetching weather data" in response_artifact.value
