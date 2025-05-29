"""
This module defines the classes and routes related to energy consumption per month and
price timeband (peak, flat, valley)

Classes:
    EnergyConsumptionBase: Base class to represent energy consumption data.
    EnergyConsumption: Class to represent the table model of energy consumption.
    EnergyConsumptionPublic: Class to represent the data model of energy consumption returned in queries.
    EnergyConsumptionCreate: Class to represent the data model of energy consumption to be created.

Routes:
    create_energy_consumption: Creates a new energy consumption entry.
    read_energy_consumptions_by_project: Retrieves all energy consumption entries for a specific project.
"""
from fastapi import APIRouter
from sqlmodel import SQLModel, Field, select, delete

import id_factory
from db import SessionDep


class EnergyConsumptionBase(SQLModel):
    """
    Base class to represent energy consumption data.

    Attributes:
        month (int): Month of the energy consumption data.
        peak (int): Peak energy consumption.
        flat (int): Flat energy consumption.
        valley (int): Valley energy consumption.
        project_id (str): Foreign key referencing the associated project.
    """
    month: int
    peak: int
    flat: int
    valley: int
    project_id: str = Field(foreign_key="projectinfo.id", index=True)

class EnergyConsumption(EnergyConsumptionBase, table=True):
    """
    Class to represent the table model of energy consumption.

    Attributes:
        id (str): Energy consumption ID.
    """
    id: str | None = Field(default_factory=id_factory.generate_uuid, primary_key=True)

class EnergyConsumptionPublic(EnergyConsumptionBase):
    """
    Class to represent the data model of energy consumption returned in queries.

    Attributes:
        id (str): Energy consumption ID.
    """
    id: str

class EnergyConsumptionCreate(EnergyConsumptionBase):
    """
    Class to represent the data model of energy consumption to be created.
    """

router = APIRouter(
    prefix="/energy_consumption",
    responses={404: {"description": "No energy consumption data was found for the given project ID."}},
)

@router.post('/', response_model=list[EnergyConsumptionPublic])
def create_energy_consumptions(project_id: str, energy_consumptions: list[EnergyConsumptionCreate], session: SessionDep) -> list[EnergyConsumption]:
    """
    Replace all energy consumption entries for a specific project.

    Args:
        project_id (str): The ID of the project to associate the energy consumption entries with.
        energy_consumptions (list[EnergyConsumptionCreate]): List of energy consumption data.
        session (SessionDep): Database session.

    Returns:
        list[EnergyConsumption]: List of created energy consumption data.
    """
    # Delete existing energy consumption entries for the project
    session.exec(delete(EnergyConsumption).where(EnergyConsumption.project_id == project_id))
    session.commit()

    # Create new energy consumption entries
    db_energy_consumptions = [
        EnergyConsumption.model_validate({**entry.model_dump(), "project_id": project_id})
        for entry in energy_consumptions
    ]
    session.add_all(db_energy_consumptions)
    session.commit()
    for entry in db_energy_consumptions:
        session.refresh(entry)
    return db_energy_consumptions

@router.get('/project/{project_id}', response_model=list[EnergyConsumptionPublic])
def read_energy_consumptions_by_project(project_id: str, session: SessionDep):
    """
    Retrieve all energy consumption entries for a specific project.

    Args:
        project_id (str): The ID of the project to retrieve energy consumption data for.
        session (SessionDep): Database session.

    Returns:
        list[EnergyConsumptionPublic]: List of all energy consumption entries for the project.
    """
    energy_consumptions = session.exec(select(EnergyConsumption).where(EnergyConsumption.project_id == project_id)).all()
    if not energy_consumptions:
        return []
    return energy_consumptions
