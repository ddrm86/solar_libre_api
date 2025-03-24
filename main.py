"""
This module initializes and configures the FastAPI application for the SolarLibre API.

It sets up the database, includes the necessary routers, and defines the root endpoint.
"""
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

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

origins = [
    "http://localhost:8080",
]
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
