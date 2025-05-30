"""
This module defines the classes and routes related to string setups.

Classes:
    StringSetupBase: Base class to represent string setup data.
    StringSetup: Class to represent the table model of string setups.
    StringSetupPublic: Class to represent the data model of string setups returned in queries.
    StringSetupCreate: Class to represent the data model of string setups to be created.

Routes:
    create_string_setups: Creates new string setup entries for an MPPT setup.
    read_string_setups_by_mppt_setup: Retrieves all string setup entries for a specific MPPT setup.
"""
from fastapi import APIRouter
from sqlmodel import SQLModel, Field, select, delete

import id_factory
from db import SessionDep


class StringSetupBase(SQLModel):
    """
    Base class to represent string setup data.

    Attributes:
        panel_number (int | None): Number of panels in the string setup.
        solar_array (str | None): Foreign key referencing the associated solar array.
        mppt_setup_id (str): Foreign key referencing the associated MPPT setup.
    """
    panel_number: int | None = None
    solar_array: str | None = Field(default=None, foreign_key="solararray.id", index=True)
    mppt_setup_id: str = Field(foreign_key="mpptsetup.id", index=True)


class StringSetup(StringSetupBase, table=True):
    """
    Class to represent the table model of string setups.

    Attributes:
        id (str): String setup ID.
    """
    id: str | None = Field(default_factory=id_factory.generate_uuid, primary_key=True)


class StringSetupPublic(StringSetupBase):
    """
    Class to represent the data model of string setups returned in queries.

    Attributes:
        id (str): String setup ID.
    """
    id: str


class StringSetupCreate(StringSetupBase):
    """
    Class to represent the data model of string setups to be created.
    """


router = APIRouter(
    prefix="/string_setups",
    responses={404: {"description": "No string setup data was found for the given MPPT setup ID."}},
)


@router.post('/', response_model=list[StringSetupPublic])
def create_string_setups(mppt_setup_id: str, string_setups: list[StringSetupCreate], session: SessionDep) -> list[StringSetup]:
    """
    Replace all string setup entries for a specific MPPT setup.

    Args:
        mppt_setup_id (str): The ID of the MPPT setup to associate the string setup entries with.
        string_setups (list[StringSetupCreate]): List of string setup data.
        session (SessionDep): Database session.

    Returns:
        list[StringSetup]: List of created string setup data.
    """
    # Delete existing string setup entries for the MPPT setup
    session.exec(delete(StringSetup).where(StringSetup.mppt_setup_id == mppt_setup_id))
    session.commit()

    # Create new string setup entries
    db_string_setups = [
        StringSetup.model_validate({**entry.model_dump(), "mppt_setup_id": mppt_setup_id})
        for entry in string_setups
    ]
    session.add_all(db_string_setups)
    session.commit()
    for entry in db_string_setups:
        session.refresh(entry)
    return db_string_setups


@router.get('/mppt_setup/{mppt_setup_id}', response_model=list[StringSetupPublic])
def read_string_setups_by_mppt_setup(mppt_setup_id: str, session: SessionDep):
    """
    Retrieve all string setup entries for a specific MPPT setup.

    Args:
        mppt_setup_id (str): The ID of the MPPT setup to retrieve string setup data for.
        session (SessionDep): Database session.

    Returns:
        list[StringSetupPublic]: List of all string setup entries for the MPPT setup.
    """
    string_setups = session.exec(select(StringSetup).where(StringSetup.mppt_setup_id == mppt_setup_id)).all()
    if not string_setups:
        return []
    return string_setups
