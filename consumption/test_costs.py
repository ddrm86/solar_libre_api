import math

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from consumption.costs import Costs
from db import get_session
from main import app


@pytest.fixture(name='session')
def session_fixture():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name='client')
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_create_costs(client: TestClient):
    response = client.post('/costs/', json={
        'vat': 21.0,
        'electric_tax': 5.0,
        'peak_kwh_cost': 0.2,
        'flat_kwh_cost': 0.15,
        'valley_kwh_cost': 0.1,
        'total_annual_cost': 1200.0,
        'compensation_per_kwh': 0.05,
        'installation_cost': 5000.0,
        'maintenance_cost': 200.0,
        'inflation': 2.0,
        'project_id': 'proj_1'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['project_id'] == 'proj_1'
    assert math.isclose(data['vat'], 21.0, rel_tol=1e-9, abs_tol=1e-9)
    assert 'id' in data

def test_update_costs(client: TestClient, session: Session):
    costs = Costs(
        vat=21.0,
        electric_tax=5.0,
        peak_kwh_cost=0.2,
        flat_kwh_cost=0.15,
        valley_kwh_cost=0.1,
        total_annual_cost=1200.0,
        compensation_per_kwh=0.05,
        installation_cost=5000.0,
        maintenance_cost=200.0,
        inflation=2.0,
        project_id='proj_1'
    )
    session.add(costs)
    session.commit()
    session.refresh(costs)

    response = client.post('/costs/', json={
        'vat': 10.0,
        'electric_tax': 3.0,
        'peak_kwh_cost': 0.18,
        'flat_kwh_cost': 0.13,
        'valley_kwh_cost': 0.09,
        'total_annual_cost': 1000.0,
        'compensation_per_kwh': 0.04,
        'installation_cost': 4000.0,
        'maintenance_cost': 150.0,
        'inflation': 1.5,
        'project_id': 'proj_1'
    })
    assert response.status_code == 200
    data = response.json()
    assert math.isclose(data['vat'], 10.0, rel_tol=1e-9, abs_tol=1e-9)
    assert data['project_id'] == 'proj_1'

def test_get_costs_by_project(client: TestClient, session: Session):
    costs = Costs(
        vat=21.0,
        electric_tax=5.0,
        peak_kwh_cost=0.2,
        flat_kwh_cost=0.15,
        valley_kwh_cost=0.1,
        total_annual_cost=1200.0,
        compensation_per_kwh=0.05,
        installation_cost=5000.0,
        maintenance_cost=200.0,
        inflation=2.0,
        project_id='proj_1'
    )
    session.add(costs)
    session.commit()
    session.refresh(costs)

    response = client.get('/costs/proj_1')
    assert response.status_code == 200
    data = response.json()
    assert data['project_id'] == 'proj_1'
    assert math.isclose(data['vat'], 21.0, rel_tol=1e-9, abs_tol=1e-9)

def test_get_costs_by_project_not_found(client: TestClient):
    response = client.get('/costs/nonexistent_project')
    assert response.status_code == 404 or response.status_code == 422
