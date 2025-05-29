"""
This module defines the classes and routes related to solar arrays.

Classes:
    SolarArrayBase: Base class to represent solar array data.
    SolarArray: Class to represent the table model of solar arrays.
    SolarArrayPublic: Class to represent the data model of solar arrays returned in queries.
    SolarArrayCreate: Class to represent the data model of solar arrays to be created.

Routes:
    create_solar_arrays: Creates new solar array entries for a project.
    read_solar_arrays_by_project: Retrieves all solar array entries for a specific project.
"""
from fastapi import APIRouter
from sqlmodel import SQLModel, Field, select, delete

import id_factory
from db import SessionDep


class SolarArrayBase(SQLModel):
    """
    Base class to represent solar array data.

    Attributes:
        angle (int): Tilt angle of the solar array.
        azimuth (int): Azimuth angle of the solar array.
        loss (int): Loss percentage of the solar array.
        panel_number (int): Number of panels in the solar array.
        is_dirty (bool): Indicates if the solar array is dirty.
        panel (str | None): Optional foreign key referencing the associated panel.
        project_id (str): Foreign key referencing the associated project.
    """
    angle: int
    azimuth: int
    loss: int
    panel_number: int
    is_dirty: bool
    panel: str | None = Field(default=None, foreign_key="panel.id", index=True)
    project_id: str = Field(foreign_key="projectinfo.id", index=True)


class SolarArray(SolarArrayBase, table=True):
    """
    Class to represent the table model of solar arrays.

    Attributes:
        id (str): Solar array ID.
    """
    id: str | None = Field(default_factory=id_factory.generate_uuid, primary_key=True)


class SolarArrayPublic(SolarArrayBase):
    """
    Class to represent the data model of solar arrays returned in queries.

    Attributes:
        id (str): Solar array ID.
    """
    id: str


class SolarArrayCreate(SolarArrayBase):
    """
    Class to represent the data model of solar arrays to be created.
    """


router = APIRouter(
    prefix="/solar_arrays",
    responses={404: {"description": "No solar array data was found for the given project ID."}},
)


@router.post('/', response_model=list[SolarArrayPublic])
def create_solar_arrays(project_id: str, solar_arrays: list[SolarArrayCreate], session: SessionDep) -> list[SolarArray]:
    """
    Replace all solar array entries for a specific project.

    Args:
        project_id (str): The ID of the project to associate the solar array entries with.
        solar_arrays (list[SolarArrayCreate]): List of solar array data.
        session (SessionDep): Database session.

    Returns:
        list[SolarArray]: List of created solar array data.
    """
    # Delete existing solar array entries for the project
    session.exec(delete(SolarArray).where(SolarArray.project_id == project_id))
    session.commit()

    # Create new solar array entries
    db_solar_arrays = [
        SolarArray.model_validate({**entry.model_dump(), "project_id": project_id})
        for entry in solar_arrays
    ]
    session.add_all(db_solar_arrays)
    session.commit()
    for entry in db_solar_arrays:
        session.refresh(entry)
    return db_solar_arrays


@router.get('/project/{project_id}', response_model=list[SolarArrayPublic])
def read_solar_arrays_by_project(project_id: str, session: SessionDep):
    """
    Retrieve all solar array entries for a specific project.

    Args:
        project_id (str): The ID of the project to retrieve solar array data for.
        session (SessionDep): Database session.

    Returns:
        list[SolarArrayPublic]: List of all solar array entries for the project.
    """
    solar_arrays = session.exec(select(SolarArray).where(SolarArray.project_id == project_id)).all()
    if not solar_arrays:
        return []
    return solar_arrays
