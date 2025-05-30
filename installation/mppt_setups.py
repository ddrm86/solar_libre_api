"""
This module defines the classes and routes related to MPPT setups.

Classes:
    MPPTSetupBase: Base class to represent MPPT setup data.
    MPPTSetup: Class to represent the table model of MPPT setups.
    MPPTSetupPublic: Class to represent the data model of MPPT setups returned in queries.
    MPPTSetupCreate: Class to represent the data model of MPPT setups to be created.

Routes:
    create_mppt_setups: Creates new MPPT setup entries for an inverter setup.
    read_mppt_setups_by_inverter_setup: Retrieves all MPPT setup entries for a specific inverter setup.
"""
from fastapi import APIRouter
from sqlmodel import SQLModel, Field, select, delete

import id_factory
from db import SessionDep


class MPPTSetupBase(SQLModel):
    """
    Base class to represent MPPT setup data.

    Attributes:
        inverter_setup_id (str): Foreign key referencing the associated inverter setup.
    """
    inverter_setup_id: str = Field(foreign_key="invertersetup.id", index=True)


class MPPTSetup(MPPTSetupBase, table=True):
    """
    Class to represent the table model of MPPT setups.

    Attributes:
        id (str): MPPT setup ID.
    """
    id: str | None = Field(default_factory=id_factory.generate_uuid, primary_key=True)


class MPPTSetupPublic(MPPTSetupBase):
    """
    Class to represent the data model of MPPT setups returned in queries.

    Attributes:
        id (str): MPPT setup ID.
    """
    id: str


class MPPTSetupCreate(MPPTSetupBase):
    """
    Class to represent the data model of MPPT setups to be created.
    """


router = APIRouter(
    prefix="/mppt_setups",
    responses={404: {"description": "No MPPT setup data was found for the given inverter setup ID."}},
)


@router.post('/', response_model=list[MPPTSetupPublic])
def create_mppt_setups(inverter_setup_id: str, mppt_setups: list[MPPTSetupCreate], session: SessionDep) -> list[MPPTSetup]:
    """
    Replace all MPPT setup entries for a specific inverter setup.

    Args:
        inverter_setup_id (str): The ID of the inverter setup to associate the MPPT setup entries with.
        mppt_setups (list[MPPTSetupCreate]): List of MPPT setup data.
        session (SessionDep): Database session.

    Returns:
        list[MPPTSetup]: List of created MPPT setup data.
    """
    # Delete existing MPPT setup entries for the inverter setup
    session.exec(delete(MPPTSetup).where(MPPTSetup.inverter_setup_id == inverter_setup_id))
    session.commit()

    # Create new MPPT setup entries
    db_mppt_setups = [
        MPPTSetup.model_validate({**entry.model_dump(), "inverter_setup_id": inverter_setup_id})
        for entry in mppt_setups
    ]
    session.add_all(db_mppt_setups)
    session.commit()
    for entry in db_mppt_setups:
        session.refresh(entry)
    return db_mppt_setups


@router.get('/inverter_setup/{inverter_setup_id}', response_model=list[MPPTSetupPublic])
def read_mppt_setups_by_inverter_setup(inverter_setup_id: str, session: SessionDep):
    """
    Retrieve all MPPT setup entries for a specific inverter setup.

    Args:
        inverter_setup_id (str): The ID of the inverter setup to retrieve MPPT setup data for.
        session (SessionDep): Database session.

    Returns:
        list[MPPTSetupPublic]: List of all MPPT setup entries for the inverter setup.
    """
    mppt_setups = session.exec(select(MPPTSetup).where(MPPTSetup.inverter_setup_id == inverter_setup_id)).all()
    if not mppt_setups:
        return []
    return mppt_setups
