import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from db import get_session
from inventory.panels import PANEL_NOT_FOUND_MSG
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


def test_create_panel(client: TestClient):
    response = client.post('/panels/', json={
        'model': 'SP-100',
        'nominal_power': 100,
        'vmpp': 18.0,
        'impp': 5.56,
        'voc': 22.0,
        'isc': 6.0,
        'length': 1000,
        'width': 500,
        'description': 'A 100W solar panel'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['model'] == 'SP-100'
    assert 'id' in data


def test_create_panel_with_empty_model(client: TestClient):
    response = client.post('/panels/', json={
        'model': '',
        'nominal_power': 100,
        'vmpp': 18.0,
        'impp': 5.56,
        'voc': 22.0,
        'isc': 6.0,
        'length': 1000,
        'width': 500,
        'description': 'A 100W solar panel'
    })
    assert response.status_code == 422


def test_read_panels(client: TestClient):
    client.post('/panels/', json={
        'model': 'SP-100',
        'nominal_power': 100,
        'vmpp': 18.0,
        'impp': 5.56,
        'voc': 22.0,
        'isc': 6.0,
        'length': 1000,
        'width': 500,
        'description': 'A 100W solar panel'
    })
    client.post('/panels/', json={
        'model': 'SP-200',
        'nominal_power': 200,
        'vmpp': 36.0,
        'impp': 5.56,
        'voc': 44.0,
        'isc': 6.0,
        'length': 2000,
        'width': 1000,
        'description': 'A 200W solar panel'
    })

    response = client.get('/panels/')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['model'] == 'SP-100'
    assert data[1]['model'] == 'SP-200'


def test_read_panel(client: TestClient):
    response = client.post('/panels/', json={
        'model': 'SP-100',
        'nominal_power': 100,
        'vmpp': 18.0,
        'impp': 5.56,
        'voc': 22.0,
        'isc': 6.0,
        'length': 1000,
        'width': 500,
        'description': 'A 100W solar panel'
    })
    panel_id = response.json()['id']

    response = client.get(f'/panels/{panel_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['model'] == 'SP-100'
    assert data['id'] == panel_id


def test_read_nonexistent_panel(client: TestClient):
    response = client.get('/panels/nonexistent_id')
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == PANEL_NOT_FOUND_MSG


def test_update_panel(client: TestClient):
    response = client.post('/panels/', json={
        'model': 'SP-100',
        'nominal_power': 100,
        'vmpp': 18.0,
        'impp': 5.56,
        'voc': 22.0,
        'isc': 6.0,
        'length': 1000,
        'width': 500,
        'description': 'A 100W solar panel'
    })
    panel_id = response.json()['id']

    response = client.patch(f'/panels/{panel_id}',
                            json={'description': 'An updated 100W solar panel'})
    assert response.status_code == 200
    data = response.json()
    assert data['description'] == 'An updated 100W solar panel'
    assert data['id'] == panel_id


def test_delete_panel(client: TestClient):
    response = client.post('/panels/', json={
        'model': 'SP-100',
        'nominal_power': 100,
        'vmpp': 18.0,
        'impp': 5.56,
        'voc': 22.0,
        'isc': 6.0,
        'length': 1000,
        'width': 500,
        'description': 'A 100W solar panel'
    })
    panel_id = response.json()['id']

    response = client.delete(f'/panels/{panel_id}')
    assert response.status_code == 200
    data = response.json()
    assert data == {'id': panel_id, 'deleted': True}

    response = client.get(f'/panels/{panel_id}')
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == PANEL_NOT_FOUND_MSG


def test_update_nonexistent_panel(client: TestClient):
    response = client.patch('/panels/nonexistent_id',
                            json={'description': 'An updated 100W solar panel'})
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == PANEL_NOT_FOUND_MSG


def test_delete_nonexistent_panel(client: TestClient):
    response = client.delete('/panels/nonexistent_id')
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == PANEL_NOT_FOUND_MSG
