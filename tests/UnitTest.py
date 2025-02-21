import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_furniture(client):
    response = client.get('/api/furniture')
    assert response.status_code == 200

def test_register_user(client):
    response = client.post('/api/users', json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "password123"
    })
    assert response.status_code == 201

def test_create_order(client):
    response = client.post('/api/orders', json={
        "user_email": "test@example.com",
        "items": [{"furniture_id": 1, "quantity": 2}],
        "total": 500
    })
    assert response.status_code == 201
