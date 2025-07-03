import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from db import get_session
from installation.inverter_setups import InverterSetup
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

def test_create_inverter_setups(client: TestClient):
    response = client.post(
        '/inverter_setups/?project_id=proj_1',
        json=[
            {'inverter': 'inv_1', 'project_id': 'proj_1'},
            {'inverter': None, 'project_id': 'proj_1'}
        ]
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['project_id'] == 'proj_1'
    assert data[1]['inverter'] is None

def test_create_inverter_setups_replace_existing(client: TestClient, session: Session):
    session.add_all([
        InverterSetup(inverter='inv_1', project_id='proj_1'),
        InverterSetup(inverter='inv_2', project_id='proj_1')
    ])
    session.commit()

    response = client.post(
        '/inverter_setups/?project_id=proj_1',
        json=[
            {'inverter': 'inv_3', 'project_id': 'proj_1'}
        ]
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['inverter'] == 'inv_3'
    assert data[0]['project_id'] == 'proj_1'

def test_read_inverter_setups_by_project(client: TestClient, session: Session):
    session.add_all([
        InverterSetup(inverter='inv_1', project_id='proj_1'),
        InverterSetup(inverter=None, project_id='proj_1')
    ])
    session.commit()

    response = client.get('/inverter_setups/project/proj_1')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(d['project_id'] == 'proj_1' for d in data)

def test_read_inverter_setups_by_project_empty(client: TestClient):
    response = client.get('/inverter_setups/project/proj_2')
    assert response.status_code == 200
    data = response.json()
    assert data == []
