"""
This module defines the classes and routes related to project information.

Classes:
    ProjectInfoBase: Base class to represent project information.
    ProjectInfo: Class to represent the table model of project information.
    ProjectInfoPublic: Class to represent the data model of project information returned in queries.
    ProjectInfoCreate: Class to represent the data model of project information to be created.
    ProjectInfoUpdate: Class to represent the data model of project information to be updated.

Routes:
    create_project_info: Creates a new project information entry.
    read_project_infos: Retrieves all project information entries.
    read_project_info: Retrieves project information by its ID.
    update_project_info: Updates project information.
    delete_project_info: Deletes project information (soft).
"""
from sqlmodel import SQLModel, Field, select
from fastapi import APIRouter, HTTPException
import id_factory
from db import SessionDep


class ProjectInfoBase(SQLModel):
    """
    Base class to represent project information.

    Attributes:
        name (str): Project name.
        latitude (float): Latitude of the project location.
        longitude (float): Longitude of the project location.
        address (str | None): Optional address of the project.
        deleted (bool): Flag to mark the project as deleted.
    """
    name: str = Field(index=True, unique=True, min_length=1)
    latitude: float
    longitude: float
    address: str | None = None
    deleted: bool = Field(default=False)


class ProjectInfo(ProjectInfoBase, table=True):
    """
    Class to represent the table model of project information.

    Attributes:
        id (str): Project ID.
    """
    id: str | None = Field(default_factory=id_factory.generate_uuid, primary_key=True)


class ProjectInfoPublic(ProjectInfoBase):
    """
    Class to represent the data model of project information returned in queries.

    Attributes:
        id (str): Project ID.
    """
    id: str


class ProjectInfoCreate(ProjectInfoBase):
    """
    Class to represent the data model of project information to be created.
    """


class ProjectInfoUpdate(ProjectInfoBase):
    """
    Class to represent the data model of project information to be updated.

    Attributes:
        name (str | None): Project name.
        latitude (float | None): Latitude of the project location.
        longitude (float | None): Longitude of the project location.
        address (str | None): Optional address of the project.
    """
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None


PROJECT_INFO_NOT_FOUND_MSG: str = 'Project information not found'

router = APIRouter(
    prefix="/project_info",
    responses={404: {"description": "No project information was found with the given ID."}},
)


@router.post('/', response_model=ProjectInfoPublic)
def create_project_info(project_info: ProjectInfoCreate, session: SessionDep) -> ProjectInfo:
    """
    Create a new project information entry.

    Args:
        project_info (ProjectInfoCreate): Project information data.
        session (SessionDep): Database session.

    Returns:
        ProjectInfo: Project information data.
    """
    db_project_info = ProjectInfo.model_validate(project_info)
    session.add(db_project_info)
    session.commit()
    session.refresh(db_project_info)
    return db_project_info


@router.get('/', response_model=list[ProjectInfoPublic])
def read_project_infos(session: SessionDep):
    """
    Retrieve all project information entries.

    Args:
        session (SessionDep): Database session.

    Returns:
        list[ProjectInfoPublic]: List of all project information entries.
    """
    project_infos = session.exec(select(ProjectInfo)).all()
    return project_infos


@router.get('/{project_info_id}', response_model=ProjectInfoPublic)
def read_project_info(project_info_id: str, session: SessionDep):
    """
    Retrieve project information by its ID.

    Args:
        project_info_id (str): The ID of the project information to retrieve.
        session (SessionDep): Database session.

    Returns:
        ProjectInfoPublic: The project information data.

    Raises:
        HTTPException: If the project information with the given ID is not found.
    """
    project_info = session.get(ProjectInfo, project_info_id)
    if not project_info:
        raise HTTPException(status_code=404, detail=PROJECT_INFO_NOT_FOUND_MSG)
    return project_info


@router.patch('/{project_info_id}', response_model=ProjectInfoPublic)
def update_project_info(project_info_id: str, project_info: ProjectInfoUpdate, session: SessionDep):
    """
    Update project information.

    Args:
        project_info_id (str): The ID of the project information to update.
        project_info (ProjectInfoUpdate): The updated project information data.
        session (SessionDep): Database session.

    Returns:
        ProjectInfoPublic: The updated project information data.

    Raises:
        HTTPException: If the project information with the given ID is not found.
    """
    db_project_info = session.get(ProjectInfo, project_info_id)
    if not db_project_info:
        raise HTTPException(status_code=404, detail=PROJECT_INFO_NOT_FOUND_MSG)
    project_info_data = project_info.model_dump(exclude_unset=True)
    db_project_info.sqlmodel_update(project_info_data)
    session.add(db_project_info)
    session.commit()
    session.refresh(db_project_info)
    return db_project_info


@router.delete('/{project_info_id}')
def delete_project_info(project_info_id: str, session: SessionDep):
    """
    Flags project information as deleted.

    Args:
        project_info_id (str): The ID of the project information to delete.
        session (SessionDep): Database session.

    Returns:
        dict: Confirmation of deletion.

    Raises:
        HTTPException: If the project information with the given ID is not found.
    """
    project_info = session.get(ProjectInfo, project_info_id)
    if not project_info:
        raise HTTPException(status_code=404, detail=PROJECT_INFO_NOT_FOUND_MSG)
    project_info.deleted = True
    session.add(project_info)
    session.commit()
    session.refresh(project_info)
    return {'id': project_info_id, 'deleted': True}
