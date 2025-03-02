"""
This module handles the database setup and session management for the SolarLibre API.

It configures the SQLite database, creates the necessary tables, and provides functions
to manage database sessions.

Functions:
    create_db_and_tables(): Creates the database and required tables.
    get_session(): Provides a database session for dependency injection.
"""
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

SQLITE_FILE_NAME = 'solar_libre.db'
SQLITE_URL = f'sqlite:///{SQLITE_FILE_NAME}'

connect_args = {'check_same_thread': False}
engine = create_engine(SQLITE_URL, connect_args=connect_args)

def create_db_and_tables():
    """
    Create the database and required tables.
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Provide a database session for dependency injection.
    """
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
