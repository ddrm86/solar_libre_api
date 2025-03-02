from sqlmodel import SQLModel, Field
import id_factory


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
