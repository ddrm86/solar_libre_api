from sqlmodel import SQLModel, Field


class PanelBase(SQLModel):
    """
    Base class to represent a solar panel.

    Attributes:
        model (str): Panel model, indexed and unique.
        nominal_power (int): Nominal power of the panel.
        vmpp (float): Voltage at maximum power point.
        impp (float): Current at maximum power point.
        voc (float): Open circuit voltage.
        isc (float): Short circuit current.
        length (int): Length of the panel (mm).
        width (int): Width of the panel (mm).
        reference (str | None): Optional reference of the panel, indexed and unique.
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
