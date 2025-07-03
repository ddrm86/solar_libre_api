import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from db import get_session
from installation.mppt_setups import MPPTSetup
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

def test_create_mppt_setups(client: TestClient):
    response = client.post(
        '/mppt_setups/?inverter_setup_id=inv_1',
        json=[
            {'inverter_setup_id': 'inv_1'},
            {'inverter_setup_id': 'inv_1'}
        ]
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(d['inverter_setup_id'] == 'inv_1' for d in data)

def test_create_mppt_setups_replace_existing(client: TestClient, session: Session):
    session.add_all([
        MPPTSetup(inverter_setup_id='inv_1'),
        MPPTSetup(inverter_setup_id='inv_1')
    ])
    session.commit()

    response = client.post(
        '/mppt_setups/?inverter_setup_id=inv_1',
        json=[
            {'inverter_setup_id': 'inv_1'}
        ]
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['inverter_setup_id'] == 'inv_1'

def test_read_mppt_setups_by_inverter_setup(client: TestClient, session: Session):
    session.add_all([
        MPPTSetup(inverter_setup_id='inv_1'),
        MPPTSetup(inverter_setup_id='inv_1')
    ])
    session.commit()

    response = client.get('/mppt_setups/inverter_setup/inv_1')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(d['inverter_setup_id'] == 'inv_1' for d in data)

def test_read_mppt_setups_by_inverter_setup_empty(client: TestClient):
    response = client.get('/mppt_setups/inverter_setup/inv_2')
    assert response.status_code == 200
    data = response.json()
    assert data == []
