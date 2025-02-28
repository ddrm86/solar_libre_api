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
        length (int): Length of the panel.
        width (int): Width of the panel.
        numide (int): Identification number of the panel.
        description (str): Description of the panel.
    """
    model: str = Field(index=True, unique=True)
    nominal_power: int
    vmpp: float
    impp: float
    voc: float
    isc: float
    length: int
    width: int
    numide: int
    description: str
