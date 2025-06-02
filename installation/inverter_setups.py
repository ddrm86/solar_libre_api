"""
This module defines the classes and routes related to inverter setups.

Classes:
    InverterSetupBase: Base class to represent inverter setup data.
    InverterSetup: Class to represent the table model of inverter setups.
    InverterSetupPublic: Class to represent the data model of inverter setups returned in queries.
    InverterSetupCreate: Class to represent the data model of inverter setups to be created.

Routes:
    create_inverter_setups: Creates new inverter setup entries for a project.
    read_inverter_setups_by_project: Retrieves all inverter setup entries for a specific project.
"""
from fastapi import APIRouter
from sqlmodel import SQLModel, Field, select, delete

import id_factory
from db import SessionDep


class InverterSetupBase(SQLModel):
    """
    Base class to represent inverter setup data.

    Attributes:
        inverter (str | None): Optional foreign key referencing the associated monophase inverter.
        project_id (str): Foreign key referencing the associated project.
    """
    inverter: str | None = Field(default=None, foreign_key="monophaseinverter.id", index=True)
    project_id: str = Field(foreign_key="projectinfo.id", index=True)


class InverterSetup(InverterSetupBase, table=True):
    """
    Class to represent the table model of inverter setups.

    Attributes:
        id (str): Inverter setup ID.
    """
    id: str | None = Field(default_factory=id_factory.generate_uuid, primary_key=True)


class InverterSetupPublic(InverterSetupBase):
    """
    Class to represent the data model of inverter setups returned in queries.

    Attributes:
        id (str): Inverter setup ID.
    """
    id: str


class InverterSetupCreate(InverterSetupBase):
    """
    Class to represent the data model of inverter setups to be created.
    """


router = APIRouter(
    prefix="/inverter_setups",
    responses={404: {"description": "No inverter setup data was found for the given project ID."}},
)


@router.post('/', response_model=list[InverterSetupPublic])
def create_inverter_setups(project_id: str, inverter_setups: list[InverterSetupCreate], session: SessionDep) -> list[InverterSetup]:
    """
    Replace all inverter setup entries for a specific project.

    Args:
        project_id (str): The ID of the project to associate the inverter setup entries with.
        inverter_setups (list[InverterSetupCreate]): List of inverter setup data.
        session (SessionDep): Database session.

    Returns:
        list[InverterSetup]: List of created inverter setup data.
    """
    # Delete existing inverter setup entries for the project
    session.exec(delete(InverterSetup).where(InverterSetup.project_id == project_id))
    session.commit()

    # Create new inverter setup entries
    db_inverter_setups = [
        InverterSetup.model_validate({**entry.model_dump(), "project_id": project_id})
        for entry in inverter_setups
    ]
    session.add_all(db_inverter_setups)
    session.commit()
    for entry in db_inverter_setups:
        session.refresh(entry)
    return db_inverter_setups


@router.get('/project/{project_id}', response_model=list[InverterSetupPublic])
def read_inverter_setups_by_project(project_id: str, session: SessionDep):
    """
    Retrieve all inverter setup entries for a specific project.

    Args:
        project_id (str): The ID of the project to retrieve inverter setup data for.
        session (SessionDep): Database session.

    Returns:
        list[InverterSetupPublic]: List of all inverter setup entries for the project.
    """
    inverter_setups = session.exec(select(InverterSetup).where(InverterSetup.project_id == project_id)).all()
    if not inverter_setups:
        return []
    return inverter_setups
