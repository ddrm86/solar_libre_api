import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from db import get_session
from main import app
from consumption.energy_consumption import EnergyConsumption

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


def test_create_energy_consumptions(client: TestClient):
    response = client.post('/energy_consumption/', json={
        'project_id': 'project_1',
        'energy_consumptions': [
            {'month': 1, 'peak': 100, 'flat': 200, 'valley': 300},
            {'month': 2, 'peak': 150, 'flat': 250, 'valley': 350}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['month'] == 1
    assert data[1]['month'] == 2


def test_create_energy_consumptions_replace_existing(client: TestClient, session: Session):
    # Create initial entries
    session.add_all([
        EnergyConsumption(month=1, peak=100, flat=200, valley=300, project_id='project_1'),
        EnergyConsumption(month=2, peak=150, flat=250, valley=350, project_id='project_1')
    ])
    session.commit()

    # Replace entries
    response = client.post('/energy_consumption/', json={
        'project_id': 'project_1',
        'energy_consumptions': [
            {'month': 3, 'peak': 200, 'flat': 300, 'valley': 400}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['month'] == 3


def test_read_energy_consumptions_by_project(client: TestClient, session: Session):
    session.add_all([
        EnergyConsumption(month=1, peak=100, flat=200, valley=300, project_id='project_1'),
        EnergyConsumption(month=2, peak=150, flat=250, valley=350, project_id='project_1')
    ])
    session.commit()

    response = client.get('/energy_consumption/project/project_1')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['month'] == 1
    assert data[1]['month'] == 2


def test_read_energy_consumptions_by_project_empty(client: TestClient):
    response = client.get('/energy_consumption/project/project_2')
    assert response.status_code == 200
    data = response.json()
    assert data == []
