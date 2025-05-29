import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from db import get_session
from main import app
from installation.solar_arrays import SolarArray

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


def test_create_solar_arrays(client: TestClient):
    response = client.post('/solar_arrays/', json={
        'project_id': 'project_1',
        'solar_arrays': [
            {'angle': 30, 'azimuth': 180, 'loss': 5, 'panel_number': 10, 'is_dirty': False},
            {'angle': 45, 'azimuth': 90, 'loss': 10, 'panel_number': 20, 'is_dirty': True}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['angle'] == 30
    assert data[1]['angle'] == 45


def test_create_solar_arrays_replace_existing(client: TestClient, session: Session):
    # Create initial entries
    session.add_all([
        SolarArray(angle=30, azimuth=180, loss=5, panel_number=10, is_dirty=False, project_id='project_1'),
        SolarArray(angle=45, azimuth=90, loss=10, panel_number=20, is_dirty=True, project_id='project_1')
    ])
    session.commit()

    # Replace entries
    response = client.post('/solar_arrays/', json={
        'project_id': 'project_1',
        'solar_arrays': [
            {'angle': 60, 'azimuth': 270, 'loss': 15, 'panel_number': 15, 'is_dirty': False}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['angle'] == 60


def test_read_solar_arrays_by_project(client: TestClient, session: Session):
    session.add_all([
        SolarArray(angle=30, azimuth=180, loss=5, panel_number=10, is_dirty=False, project_id='project_1'),
        SolarArray(angle=45, azimuth=90, loss=10, panel_number=20, is_dirty=True, project_id='project_1')
    ])
    session.commit()

    response = client.get('/solar_arrays/project/project_1')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['angle'] == 30
    assert data[1]['angle'] == 45


def test_read_solar_arrays_by_project_empty(client: TestClient):
    response = client.get('/solar_arrays/project/project_2')
    assert response.status_code == 200
    data = response.json()
    assert data == []
