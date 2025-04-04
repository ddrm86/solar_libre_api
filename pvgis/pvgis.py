import requests
from typing import Annotated
from fastapi import APIRouter, Query
from pydantic import BaseModel


class PVGISRequest(BaseModel):
    latitude: float
    longitude: float
    peak_power: float
    loss: float
    angle: int
    azimuth: int


router = APIRouter(
    prefix="/pvgis",
)

@router.get('/')
def get_pvgis_data(req_params: Annotated[PVGISRequest, Query()]):
    base_url = 'https://re.jrc.ec.europa.eu/api/v5_2/PVcalc'
    params = {'lat': req_params.latitude, 'lon': req_params.longitude,
              'peakpower': req_params.peak_power, 'loss': req_params.loss,
              'angle': req_params.angle, 'aspect': req_params.azimuth, 'outputformat': 'json'}
    request = requests.get(base_url, params=params, timeout=3)
    if request.status_code == 200:
        return request.json()
    else:
        return {'error': 'Error al obtener datos de PVGIS', 'status_code': request.status_code}
