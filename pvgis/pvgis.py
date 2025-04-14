"""
This module defines the router and endpoint to obtain PVGIS solar production data.

PVGIS API has to be accessed through the backend due to their CORS policy:
https://stackoverflow.com/questions/75372299/api-fetch-from-pvgis-with-javascript-node-js/
"""
from typing import Annotated
import os, requests
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel


class PVGISRequest(BaseModel):
    """
    Data model for PVGIS request parameters.

    Attributes:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        peak_power (float): Peak power of the solar panel system in kW.
        loss (float): System losses in percentage.
        angle (int): Tilt angle of the solar panels.
        azimuth (int): Azimuth angle of the solar panels (0 = S, 90 = W, -90 = E).
    """
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
    """
    Retrieve PVGIS solar production data based on the provided parameters.

    Args:
        req_params (Annotated[PVGISRequest, Query()]): Request parameters for PVGIS API.

    Returns:
        dict: JSON response from PVGIS API or an error message with status code.
    """
    base_url = 'https://re.jrc.ec.europa.eu/api/v5_3/PVcalc'
    params = {'lat': req_params.latitude, 'lon': req_params.longitude,
              'peakpower': req_params.peak_power, 'loss': req_params.loss,
              'angle': req_params.angle, 'aspect': req_params.azimuth, 'outputformat': 'json'}
    proxy_dict = {
        "http"  : os.environ.get('FIXIE_URL', ''),
    }
    request = requests.get(base_url, params=params, timeout=3, proxies=proxy_dict)
    if request.status_code != 200:
        raise HTTPException(status_code=request.status_code, detail=request.json())

    return request.json()
