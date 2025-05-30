"""
This module initializes and configures the FastAPI application for the SolarLibre API.

It sets up the database, includes the necessary routers, and defines the root endpoint.
"""
import logging
import os
import json
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler

from inventory import panels, monophase_inverters
from pvgis import pvgis
from project_info import project_info
from consumption import energy_consumption
from installation import solar_arrays, inverter_setups, mppt_setups
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
app.include_router(monophase_inverters.router)
app.include_router(pvgis.router)
app.include_router(project_info.router)
app.include_router(energy_consumption.router)
app.include_router(solar_arrays.router)
app.include_router(inverter_setups.router)
app.include_router(mppt_setups.router)


DEFAULT_CORS_ORIGINS = '["http://localhost:8080", "http://localhost:5173"]'
origins = json.loads(os.environ.get('SOLAR_LIBRE_API_ORIGINS', DEFAULT_CORS_ORIGINS))
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Exception handler for validation errors.

    Args:
        request (Request): The request that raised the exception.
        exc (RequestValidationError): The exception raised.
    """
    logging.warning('Validation error: %s - %s', request, exc)
    return await request_validation_exception_handler(request, exc)


@app.get("/")
async def root():
    """
    Root endpoint of the API.

    Returns:
        dict: A welcome message with a link to the API documentation.
    """
    return {"message": "Welcome to SolarLibre API. Visit /docs for documentation."}


if __name__ == "__main__":
    host = os.environ.get('SOLAR_LIBRE_API_HOST', '0.0.0.0')
    port = int(os.environ.get('SOLAR_LIBRE_API_PORT', 8000))
    uvicorn.run(app, host=host, port=port)
