"""
This module defines the classes and routes related to monophase inverters.

Classes:
    MonophaseInverterBase: Base class to represent a monophase inverter.
    MonophaseInverter: Class to represent the table model of a monophase inverter.
    MonophaseInverterPublic: Class to represent the data model of a monophase inverter returned in
    queries.
    MonophaseInverterCreate: Class to represent the data model of a monophase inverter to be
    created.
    MonophaseInverterUpdate: Class to represent the data model of a monophase inverter to be
    updated.

Routes:
    create_monophase_inverter: Creates a new monophase inverter.
    read_monophase_inverters: Retrieves all monophase inverters.
    read_monophase_inverter: Retrieves a monophase inverter by its ID.
    update_monophase_inverter: Updates a monophase inverter.
    delete_monophase_inverter: Flags a monophase inverter as deleted.
"""
from sqlmodel import SQLModel, Field, select
from fastapi import APIRouter, HTTPException
import id_factory
from db import SessionDep


class MonophaseInverterBase(SQLModel):
    """
    Base class to represent a monophase inverter.

    Attributes:
        maker (str): Inverter manufacturer.
        model (str): Inverter model.
        recommended_max_input_power (int): Recommended maximum input power.
        nominal_output_power (int): Nominal output power.
        max_input_voltage (int): Maximum input voltage.
        startup_voltage (int): Startup voltage.
        min_mppt_operating_voltage (int): Minimum MPPT operating voltage.
        max_mppt_operating_voltage (int): Maximum MPPT operating voltage.
        max_input_current_per_mppt (float): Maximum input current per MPPT.
        max_short_circuit_current (float): Maximum short circuit current.
        number_of_mppts (int): Number of MPPTs.
        max_inputs_per_mppt (int): Maximum inputs per MPPT.
        max_output_current (float): Maximum output current.
        reference (str | None): Optional reference of the inverter.
        description (str | None): Description of the inverter.
        deleted (bool): Flag to mark the inverter as deleted.
    """
    maker: str = Field(min_length=1)
    model: str = Field(index=True, unique=True, min_length=1)
    recommended_max_input_power: int
    nominal_output_power: int
    max_input_voltage: int
    startup_voltage: int
    min_mppt_operating_voltage: int
    max_mppt_operating_voltage: int
    max_input_current_per_mppt: float
    max_short_circuit_current: float
    number_of_mppts: int
    max_inputs_per_mppt: int
    max_output_current: float
    reference: str | None = Field(default=None, index=True, unique=True)
    description: str | None = Field(default=None)
    deleted: bool = Field(default=False)


class MonophaseInverter(MonophaseInverterBase, table=True):
    """
    Class to represent the table model of a monophase inverter.

    Attributes:
        id (str): Inverter ID.
    """
    id: str | None = Field(default_factory=id_factory.generate_uuid, primary_key=True)


class MonophaseInverterPublic(MonophaseInverterBase):
    """
    Class to represent the data model of a monophase inverter returned in queries.

    Attributes:
        id (str): Inverter ID.
    """
    id: str


class MonophaseInverterCreate(MonophaseInverterBase):
    """
    Class to represent the data model of a monophase inverter to be created.
    """


class MonophaseInverterUpdate(MonophaseInverterBase):
    """
    Class to represent the data model of a monophase inverter to be updated.

    Attributes:
        maker (str | None): Inverter manufacturer.
        model (str | None): Inverter model.
        recommended_max_input_power (int | None): Recommended maximum input power.
        nominal_output_power (int | None): Nominal output power.
        max_input_voltage (int | None): Maximum input voltage.
        startup_voltage (int | None): Startup voltage.
        min_mppt_operating_voltage (int | None): Minimum MPPT operating voltage.
        max_mppt_operating_voltage (int | None): Maximum MPPT operating voltage.
        max_input_current_per_mppt (float | None): Maximum input current per MPPT.
        max_short_circuit_current (float | None): Maximum short circuit current.
        number_of_mppts (int | None): Number of MPPTs.
        max_inputs_per_mppt (int | None): Maximum inputs per MPPT.
        max_output_current (float | None): Maximum output current.
        reference (str | None): Optional reference of the inverter.
        description (str | None): Description of the inverter.
    """
    maker: str | None = None
    model: str | None = None
    recommended_max_input_power: int | None = None
    nominal_output_power: int | None = None
    max_input_voltage: int | None = None
    startup_voltage: int | None = None
    min_mppt_operating_voltage: int | None = None
    max_mppt_operating_voltage: int | None = None
    max_input_current_per_mppt: float | None = None
    max_short_circuit_current: float | None = None
    number_of_mppts: int | None = None
    max_inputs_per_mppt: int | None = None
    max_output_current: float | None = None
    reference: str | None = None
    description: str | None = None


MONOPHASE_INVERTER_NOT_FOUND_MSG: str = 'Monophase inverter not found'

router = APIRouter(
    prefix="/monophase_inverters",
    responses={404: {"description": "No monophase inverter was found with the given ID."}},
)


@router.post('/', response_model=MonophaseInverterPublic)
def create_monophase_inverter(inverter: MonophaseInverterCreate, session: SessionDep) \
        -> MonophaseInverter:
    """
    Create a new monophase inverter.

    Args:
        inverter (MonophaseInverterCreate): Monophase inverter data.
        session (SessionDep): Database session.

    Returns:
        MonophaseInverter: Monophase inverter data.
    """
    db_inverter = MonophaseInverter.model_validate(inverter)
    session.add(db_inverter)
    session.commit()
    session.refresh(db_inverter)
    return db_inverter


@router.get('/', response_model=list[MonophaseInverterPublic])
def read_monophase_inverters(session: SessionDep):
    """
    Retrieve all monophase inverters.

    Args:
        session (SessionDep): Database session.

    Returns:
        list[MonophaseInverterPublic]: List of all monophase inverters.
    """
    inverters = session.exec(select(MonophaseInverter)).all()
    return inverters


@router.get('/{inverter_id}', response_model=MonophaseInverterPublic)
def read_monophase_inverter(inverter_id: str, session: SessionDep):
    """
    Retrieve a monophase inverter by its ID.

    Args:
        inverter_id (str): The ID of the monophase inverter to retrieve.
        session (SessionDep): Database session.

    Returns:
        MonophaseInverterPublic: The monophase inverter data.

    Raises:
        HTTPException: If the monophase inverter with the given ID is not found.
    """
    inverter = session.get(MonophaseInverter, inverter_id)
    if not inverter:
        raise HTTPException(status_code=404, detail=MONOPHASE_INVERTER_NOT_FOUND_MSG)
    return inverter


@router.patch('/{inverter_id}', response_model=MonophaseInverterPublic)
def update_monophase_inverter(inverter_id: str, inverter: MonophaseInverterUpdate,
                              session: SessionDep):
    """
    Update a monophase inverter.

    Args:
        inverter_id (str): The ID of the monophase inverter to update.
        inverter (MonophaseInverterUpdate): The updated monophase inverter data.
        session (SessionDep): Database session.

    Returns:
        MonophaseInverterPublic: The updated monophase inverter data.

    Raises:
        HTTPException: If the monophase inverter with the given ID is not found.
    """
    db_inverter = session.get(MonophaseInverter, inverter_id)
    if not db_inverter:
        raise HTTPException(status_code=404, detail=MONOPHASE_INVERTER_NOT_FOUND_MSG)
    inverter_data = inverter.model_dump(exclude_unset=True)
    db_inverter.sqlmodel_update(inverter_data)
    session.add(db_inverter)
    session.commit()
    session.refresh(db_inverter)
    return db_inverter


@router.delete('/{inverter_id}')
def delete_monophase_inverter(inverter_id: str, session: SessionDep):
    """
    Flags a monophase inverter as deleted.

    Args:
        inverter_id (str): The ID of the monophase inverter to delete.
        session (SessionDep): Database session.

    Returns:
        dict: Confirmation of deletion.

    Raises:
        HTTPException: If the monophase inverter with the given ID is not found.
    """
    inverter = session.get(MonophaseInverter, inverter_id)
    if not inverter:
        raise HTTPException(status_code=404, detail=MONOPHASE_INVERTER_NOT_FOUND_MSG)
    inverter.deleted = True
    session.add(inverter)
    session.commit()
    session.refresh(inverter)
    return {'id': inverter_id, 'deleted': True}
