import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def pvgis_request_params():
    return {
        "latitude": 40.0,
        "longitude": -3.0,
        "peak_power": 5.0,
        "loss": 10.0,
        "angle": 30,
        "azimuth": 0
    }

def test_get_pvgis_data(pvgis_request_params):
    response = client.get('/pvgis/', params=pvgis_request_params)
    assert response.status_code == 200
    data = response.json()
    assert "outputs" in data
    assert "monthly" in data["outputs"]

def test_get_pvgis_data_invalid_params():
    response = client.get('/pvgis/', params={})
    assert response.status_code == 422
