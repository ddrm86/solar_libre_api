from pydantic import BaseModel
from fastapi import APIRouter

class PVGISRequest(BaseModel):
    latitude: float
    longitude: float
    peak_power: float
    loss: float
    angle: int
    azimuth: int


class PVGISResponse(BaseModel):
    pass

router = APIRouter(
    prefix="/pvgis",
)

@router.get('/', response_model=PVGISResponse)
def get_pvgis_data(request: PVGISRequest):
    return PVGISResponse()
