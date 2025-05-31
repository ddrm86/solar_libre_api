"""
This module defines the classes and routes related to project costs.

Classes:
    CostsBase: Base class to represent project costs.
    Costs: Class to represent the table model of project costs.
    CostsPublic: Class to represent the data model of project costs returned in queries.
    CostsCreate: Class to represent the data model of project costs to be created or updated.

Routes:
    get_costs_by_project: Retrieves the costs associated with a project by its ID.
    upsert_costs: Adds or updates the costs associated with a project.
"""
from sqlmodel import SQLModel, Field, select
from fastapi import APIRouter, HTTPException
import id_factory
from db import SessionDep


class CostsBase(SQLModel):
    """
    Base class to represent project costs.

    Attributes:
        vat (float): VAT percentage.
        electric_tax (float): Electric tax percentage.
        peak_kwh_cost (float): Cost per kWh during peak hours.
        flat_kwh_cost (float): Cost per kWh during flat hours.
        valley_kwh_cost (float): Cost per kWh during valley hours.
        total_annual_cost (float): Total annual cost.
        compensation_per_kwh (float): Compensation per kWh.
        installation_cost (float): Installation cost.
        maintenance_cost (float): Maintenance cost.
        inflation (float): Inflation percentage.
        project_id (str): Foreign key referencing the associated project.
    """
    vat: float
    electric_tax: float
    peak_kwh_cost: float
    flat_kwh_cost: float
    valley_kwh_cost: float
    total_annual_cost: float
    compensation_per_kwh: float
    installation_cost: float
    maintenance_cost: float
    inflation: float
    project_id: str = Field(foreign_key="projectinfo.id", index=True, unique=True)


class Costs(CostsBase, table=True):
    """
    Class to represent the table model of project costs.

    Attributes:
        id (str): Costs ID.
    """
    id: str | None = Field(default_factory=id_factory.generate_uuid, primary_key=True)


class CostsPublic(CostsBase):
    """
    Class to represent the data model of project costs returned in queries.

    Attributes:
        id (str): Costs ID.
    """
    id: str


class CostsCreate(CostsBase):
    """
    Class to represent the data model of project costs to be created or updated.
    """


COSTS_NOT_FOUND_MSG: str = 'Costs not found for the given project ID'

router = APIRouter(
    prefix="/costs",
    responses={404: {"description": "No costs were found for the given project ID."}},
)


@router.get('/{project_id}', response_model=CostsPublic)
def get_costs_by_project(project_id: str, session: SessionDep):
    """
    Retrieve the costs associated with a project by its ID.

    Args:
        project_id (str): The ID of the project to retrieve costs for.
        session (SessionDep): Database session.

    Returns:
        CostsPublic: The costs data.

    Raises:
        HTTPException: If no costs are found for the given project ID.
    """
    costs = session.exec(select(Costs).where(Costs.project_id == project_id)).first()
    if not costs:
        raise HTTPException(status_code=404, detail=COSTS_NOT_FOUND_MSG)
    return costs


@router.post('/', response_model=CostsPublic)
def upsert_costs(costs_data: CostsCreate, session: SessionDep):
    """
    Add or update the costs associated with a project.

    Args:
        costs_data (CostsCreate): The costs data to add or update.
        session (SessionDep): Database session.

    Returns:
        CostsPublic: The updated or newly created costs data.
    """
    existing_costs = session.exec(select(Costs)
                                  .where(Costs.project_id == costs_data.project_id)).first()
    if existing_costs:
        costs_data_dict = costs_data.model_dump(exclude_unset=True)
        existing_costs.sqlmodel_update(costs_data_dict)
        session.add(existing_costs)
        session.commit()
        session.refresh(existing_costs)
        return existing_costs

    new_costs = Costs.model_validate(costs_data)
    session.add(new_costs)
    session.commit()
    session.refresh(new_costs)
    return new_costs
