"""
This module initializes and configures the FastAPI application for the SolarLibre API.

It sets up the database, includes the necessary routers, and defines the root endpoint.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from inventory import panels
import db

@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Initialize the database and create tables.

    This function is called at the startup of the FastAPI application to ensure
    that the database and required tables are created before handling any requests.
    """
    db.create_db_and_tables()
    yield
    db.engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(panels.router)


@app.get("/")
async def root():
    """
    Root endpoint of the API.

    Returns:
        dict: A welcome message with a link to the API documentation.
    """
    return {"message": "Welcome to SolarLibre API. Visit /docs for documentation."}
