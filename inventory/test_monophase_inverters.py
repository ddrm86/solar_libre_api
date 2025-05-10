import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from db import get_session
from inventory.monophase_inverters import MONOPHASE_INVERTER_NOT_FOUND_MSG
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


def test_create_monophase_inverter(client: TestClient):
    response = client.post('/monophase_inverters/', json={
        'maker': 'Huawei',
        'model': 'SUN2000 2KTL-L1',
        'recommended_max_input_power': 3000,
        'nominal_output_power': 2000,
        'max_input_voltage': 600,
        'startup_voltage': 100,
        'min_mppt_operating_voltage': 90,
        'max_mppt_operating_voltage': 560,
        'max_input_current_per_mppt': 12.5,
        'max_short_circuit_current_per_mppt': 18,
        'number_of_mppts': 2,
        'max_inputs_per_mppt': 1,
        'max_output_current': 10,
        'reference': '302577',
        'description': 'Inversor clásico'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['model'] == 'SUN2000 2KTL-L1'
    assert 'id' in data


def test_create_monophase_inverter_with_empty_model(client: TestClient):
    response = client.post('/monophase_inverters/', json={
        'maker': 'Huawei',
        'model': '',
        'recommended_max_input_power': 3000,
        'nominal_output_power': 2000,
        'max_input_voltage': 600,
        'startup_voltage': 100,
        'min_mppt_operating_voltage': 90,
        'max_mppt_operating_voltage': 560,
        'max_input_current_per_mppt': 12.5,
        'max_short_circuit_current_per_mppt': 18,
        'number_of_mppts': 2,
        'max_inputs_per_mppt': 1,
        'max_output_current': 10,
        'reference': '302577',
        'description': 'Inversor clásico'
    })
    assert response.status_code == 422


def test_read_monophase_inverters(client: TestClient):
    client.post('/monophase_inverters/', json={
        'maker': 'Huawei',
        'model': 'SUN2000 2KTL-L1',
        'recommended_max_input_power': 3000,
        'nominal_output_power': 2000,
        'max_input_voltage': 600,
        'startup_voltage': 100,
        'min_mppt_operating_voltage': 90,
        'max_mppt_operating_voltage': 560,
        'max_input_current_per_mppt': 12.5,
        'max_short_circuit_current_per_mppt': 18,
        'number_of_mppts': 2,
        'max_inputs_per_mppt': 1,
        'max_output_current': 10,
        'reference': '302577',
        'description': 'Inversor clásico'
    })
    client.post('/monophase_inverters/', json={
        'maker': 'Huawei',
        'model': 'SUN2000 3KTL-L1',
        'recommended_max_input_power': 4000,
        'nominal_output_power': 3000,
        'max_input_voltage': 700,
        'startup_voltage': 110,
        'min_mppt_operating_voltage': 100,
        'max_mppt_operating_voltage': 600,
        'max_input_current_per_mppt': 15.0,
        'max_short_circuit_current_per_mppt': 20,
        'number_of_mppts': 2,
        'max_inputs_per_mppt': 1,
        'max_output_current': 12,
        'reference': '302578',
        'description': 'Inversor avanzado'
    })

    response = client.get('/monophase_inverters/')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['model'] == 'SUN2000 2KTL-L1'
    assert data[1]['model'] == 'SUN2000 3KTL-L1'


def test_read_monophase_inverter(client: TestClient):
    response = client.post('/monophase_inverters/', json={
        'maker': 'Huawei',
        'model': 'SUN2000 2KTL-L1',
        'recommended_max_input_power': 3000,
        'nominal_output_power': 2000,
        'max_input_voltage': 600,
        'startup_voltage': 100,
        'min_mppt_operating_voltage': 90,
        'max_mppt_operating_voltage': 560,
        'max_input_current_per_mppt': 12.5,
        'max_short_circuit_current_per_mppt': 18,
        'number_of_mppts': 2,
        'max_inputs_per_mppt': 1,
        'max_output_current': 10,
        'reference': '302577',
        'description': 'Inversor clásico'
    })
    inverter_id = response.json()['id']

    response = client.get(f'/monophase_inverters/{inverter_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['model'] == 'SUN2000 2KTL-L1'
    assert data['id'] == inverter_id


def test_read_nonexistent_monophase_inverter(client: TestClient):
    response = client.get('/monophase_inverters/nonexistent_id')
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == MONOPHASE_INVERTER_NOT_FOUND_MSG


def test_update_monophase_inverter(client: TestClient):
    response = client.post('/monophase_inverters/', json={
        'maker': 'Huawei',
        'model': 'SUN2000 2KTL-L1',
        'recommended_max_input_power': 3000,
        'nominal_output_power': 2000,
        'max_input_voltage': 600,
        'startup_voltage': 100,
        'min_mppt_operating_voltage': 90,
        'max_mppt_operating_voltage': 560,
        'max_input_current_per_mppt': 12.5,
        'max_short_circuit_current_per_mppt': 18,
        'number_of_mppts': 2,
        'max_inputs_per_mppt': 1,
        'max_output_current': 10,
        'reference': '302577',
        'description': 'Inversor clásico'
    })
    inverter_id = response.json()['id']

    response = client.patch(f'/monophase_inverters/{inverter_id}', json={'description': 'Inversor actualizado'})
    assert response.status_code == 200
    data = response.json()
    assert data['description'] == 'Inversor actualizado'
    assert data['id'] == inverter_id


def test_delete_monophase_inverter(client: TestClient):
    response = client.post('/monophase_inverters/', json={
        'maker': 'Huawei',
        'model': 'SUN2000 2KTL-L1',
        'recommended_max_input_power': 3000,
        'nominal_output_power': 2000,
        'max_input_voltage': 600,
        'startup_voltage': 100,
        'min_mppt_operating_voltage': 90,
        'max_mppt_operating_voltage': 560,
        'max_input_current_per_mppt': 12.5,
        'max_short_circuit_current_per_mppt': 18,
        'number_of_mppts': 2,
        'max_inputs_per_mppt': 1,
        'max_output_current': 10,
        'reference': '302577',
        'description': 'Inversor clásico'
    })
    inverter_id = response.json()['id']

    response = client.delete(f'/monophase_inverters/{inverter_id}')
    assert response.status_code == 200
    data = response.json()
    assert data == {'id': inverter_id, 'deleted': True}

    response = client.get(f'/monophase_inverters/{inverter_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['deleted'] == True


def test_update_nonexistent_monophase_inverter(client: TestClient):
    response = client.patch('/monophase_inverters/nonexistent_id', json={'description': 'Inversor actualizado'})
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == MONOPHASE_INVERTER_NOT_FOUND_MSG


def test_delete_nonexistent_monophase_inverter(client: TestClient):
    response = client.delete('/monophase_inverters/nonexistent_id')
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == MONOPHASE_INVERTER_NOT_FOUND_MSG
