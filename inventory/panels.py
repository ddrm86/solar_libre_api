from sqlmodel import SQLModel, Field, select
from fastapi import APIRouter, HTTPException
import id_factory
from db import SessionDep


class PanelBase(SQLModel):
    """
    Base class to represent a solar panel.

    Attributes:
        model (str): Panel model
        nominal_power (int): Nominal power of the panel.
        vmpp (float): Voltage at maximum power point.
        impp (float): Current at maximum power point.
        voc (float): Open circuit voltage.
        isc (float): Short circuit current.
        length (int): Length of the panel (mm).
        width (int): Width of the panel (mm).
        reference (str | None): Optional reference of the panel
        description (str | None): Description of the panel.
    """
    model: str = Field(index=True, unique=True)
    nominal_power: int
    vmpp: float
    impp: float
    voc: float
    isc: float
    length: int
    width: int
    reference: str | None = Field(default=None, index=True, unique=True)
    description: str | None

class Panel(PanelBase, table=True):
    """
    Class to represent the table model of a solar panel.

    Attributes:
        id (str): Panel ID
    """
    id: str | None = Field(default_factory=id_factory.generate_uuid, primary_key=True)

class PanelPublic(PanelBase):
    """
    Class to represent the data model of a solar panel returned in queries.

    Attributes:
        id (str): Panel ID
    """
    id: str

class PanelCreate(PanelBase):
    """
    Class to represent the data model of a solar panel to be created.
    """

class PanelUpdate(PanelBase):
    """
    Class to represent the data model of a solar panel to be updated.

    Attributes:
        model (str | None): Panel model
        nominal_power (int | None): Nominal power of the panel.
        vmpp (float | None): Voltage at maximum power point.
        impp (float | None): Current at maximum power point.
        voc (float | None): Open circuit voltage.
        isc (float | None): Short circuit current.
        length (int | None): Length of the panel (mm).
        width (int | None): Width of the panel (mm).
        reference (str | None): Optional reference of the panel
        description (str | None): Description of the panel.
    """
    model: str | None = None
    nominal_power: int | None = None
    vmpp: float | None = None
    impp: float | None = None
    voc: float | None = None
    isc: float | None = None
    length: int | None = None
    width: int | None = None
    reference: str | None = None
    description: str | None = None

PANEL_NOT_FOUND_MSG: str = 'Solar panel not found'

router = APIRouter(
    prefix="/panels",
    responses={404: {"description": "No solar panel was found with the given ID."}},
)


@router.post('/', response_model=PanelPublic)
def create_panel(panel: PanelCreate, session: SessionDep) -> Panel:
    """
    Create a new solar panel.

    Args:
        panel (PanelCreate): Solar panel data.
        session (SessionDep): Database session.

    Returns:
        Panel: Solar panel data.
    """
    db_panel = Panel.model_validate(panel)
    session.add(db_panel)
    session.commit()
    session.refresh(db_panel)
    return db_panel


@router.get('/', response_model=list[PanelPublic])
def read_panels(session: SessionDep):
    """
    Retrieve all solar panels.

    Args:
        session (SessionDep): Database session.

    Returns:
        list[PanelPublic]: List of all solar panels.
    """
    panels = session.exec(select(Panel)).all()
    return panels


@router.get('/{panel_id}', response_model=PanelPublic)
def read_panel(panel_id: str, session: SessionDep):
    """
    Retrieve a solar panel by its ID.

    Args:
        panel_id (str): The ID of the solar panel to retrieve.
        session (SessionDep): Database session.

    Returns:
        PanelPublic: The solar panel data.

    Raises:
        HTTPException: If the solar panel with the given ID is not found.
    """
    panel = session.get(Panel, panel_id)
    if not panel:
        raise HTTPException(status_code=404, detail=PANEL_NOT_FOUND_MSG)
    return panel


@router.patch('/{panel_id}', response_model=PanelPublic)
def update_panel(panel_id: str, panel: PanelUpdate, session: SessionDep):
    """
    Update a solar panel.

    Args:
        panel_id (str): The ID of the solar panel to update.
        panel (PanelUpdate): The updated solar panel data.
        session (SessionDep): Database session.

    Returns:
        PanelPublic: The updated solar panel data.

    Raises:
        HTTPException: If the solar panel with the given ID is not found.
    """
    db_panel = session.get(Panel, panel_id)
    if not db_panel:
        raise HTTPException(status_code=404, detail=PANEL_NOT_FOUND_MSG)
    panel_data = panel.model_dump(exclude_unset=True)
    db_panel.sqlmodel_update(panel_data)
    session.add(db_panel)
    session.commit()
    session.refresh(db_panel)
    return db_panel


@router.delete('/{panel_id}')
def delete_panel(panel_id: str, session: SessionDep):
    """
    Delete a solar panel.

    Args:
        panel_id (str): The ID of the solar panel to delete.
        session (SessionDep): Database session.

    Returns:
        dict: Confirmation of deletion.

    Raises:
        HTTPException: If the solar panel with the given ID is not found.
    """
    panel = session.get(Panel, panel_id)
    if not panel:
        raise HTTPException(status_code=404, detail=PANEL_NOT_FOUND_MSG)
    session.delete(panel)
    session.commit()
    return {'id': panel_id, 'deleted': True}
