import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from db import get_session
from project_info.project_info import PROJECT_INFO_NOT_FOUND_MSG
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


def test_create_project_info(client: TestClient):
    response = client.post('/project_info/', json={
        'name': 'Project A',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'address': 'New York, NY'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Project A'
    assert 'id' in data


def test_create_project_info_with_empty_name(client: TestClient):
    response = client.post('/project_info/', json={
        'name': '',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'address': 'New York, NY'
    })
    assert response.status_code == 422


def test_read_project_infos(client: TestClient):
    client.post('/project_info/', json={
        'name': 'Project A',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'address': 'New York, NY'
    })
    client.post('/project_info/', json={
        'name': 'Project B',
        'latitude': 34.0522,
        'longitude': -118.2437,
        'address': 'Los Angeles, CA'
    })

    response = client.get('/project_info/')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['name'] == 'Project A'
    assert data[1]['name'] == 'Project B'


def test_read_project_info(client: TestClient):
    response = client.post('/project_info/', json={
        'name': 'Project A',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'address': 'New York, NY'
    })
    project_id = response.json()['id']

    response = client.get(f'/project_info/{project_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'Project A'
    assert data['id'] == project_id


def test_read_nonexistent_project_info(client: TestClient):
    response = client.get('/project_info/nonexistent_id')
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == PROJECT_INFO_NOT_FOUND_MSG


def test_update_project_info(client: TestClient):
    response = client.post('/project_info/', json={
        'name': 'Project A',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'address': 'New York, NY'
    })
    project_id = response.json()['id']

    response = client.patch(f'/project_info/{project_id}',
                            json={'address': 'Updated Address'})
    assert response.status_code == 200
    data = response.json()
    assert data['address'] == 'Updated Address'
    assert data['id'] == project_id


def test_delete_project_info(client: TestClient):
    response = client.post('/project_info/', json={
        'name': 'Project A',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'address': 'New York, NY'
    })
    project_id = response.json()['id']

    response = client.delete(f'/project_info/{project_id}')
    assert response.status_code == 200
    data = response.json()
    assert data == {'id': project_id, 'deleted': True}

    response = client.get(f'/project_info/{project_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['deleted'] is True


def test_update_nonexistent_project_info(client: TestClient):
    response = client.patch('/project_info/nonexistent_id',
                            json={'address': 'Updated Address'})
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == PROJECT_INFO_NOT_FOUND_MSG


def test_delete_nonexistent_project_info(client: TestClient):
    response = client.delete('/project_info/nonexistent_id')
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == PROJECT_INFO_NOT_FOUND_MSG
