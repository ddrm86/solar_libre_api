import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from db import get_session
from installation.string_setups import StringSetup
from main import app

@pytest.fixture(name='session')
def session_fixture():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False},
                           poolclass=StaticPool)
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

def test_create_string_setups(client: TestClient):
    response = client.post(
        '/string_setups/?mppt_setup_id=mppt_1',
        json=[
            {'panel_number': 10, 'solar_array': None, 'mppt_setup_id': 'mppt_1'},
            {'panel_number': 12, 'solar_array': 'array_1', 'mppt_setup_id': 'mppt_1'}
        ]
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['panel_number'] == 10
    assert data[1]['solar_array'] == 'array_1'

def test_create_string_setups_replace_existing(client: TestClient, session: Session):
    session.add_all([
        StringSetup(panel_number=10, solar_array=None, mppt_setup_id='mppt_1'),
        StringSetup(panel_number=12, solar_array='array_1', mppt_setup_id='mppt_1')
    ])
    session.commit()

    response = client.post(
        '/string_setups/?mppt_setup_id=mppt_1',
        json=[
            {'panel_number': 20, 'solar_array': 'array_2', 'mppt_setup_id': 'mppt_1'}
        ]
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['panel_number'] == 20
    assert data[0]['solar_array'] == 'array_2'

def test_read_string_setups_by_mppt_setup(client: TestClient, session: Session):
    session.add_all([
        StringSetup(panel_number=10, solar_array=None, mppt_setup_id='mppt_1'),
        StringSetup(panel_number=12, solar_array='array_1', mppt_setup_id='mppt_1')
    ])
    session.commit()

    response = client.get('/string_setups/mppt_setup/mppt_1')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['panel_number'] == 10
    assert data[1]['solar_array'] == 'array_1'

def test_read_string_setups_by_mppt_setup_empty(client: TestClient):
    response = client.get('/string_setups/mppt_setup/mppt_2')
    assert response.status_code == 200
    data = response.json()
    assert data == []
