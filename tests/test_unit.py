# tests/unit.py
import uuid
def test_get_furniture(client):
    response = client.get('/api/furniture')
    assert response.status_code == 200


def test_register_and_delete_user(client):
    # Generate a unique email for the test
    unique_email = f"test_{uuid.uuid4()}@example.com"
    
    # Register the user with the unique email
    response = client.post('/api/users', json={
        "email": unique_email,
        "name": "Test User",
        "password": "password123"
    })
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    # Optionally verify the user is in the list
    response = client.get('/api/users')
    users = response.get_json()
    user = next((u for u in users if u["email"] == unique_email), None)
    assert user is not None, "User was not found after registration"

    # Delete the user
    response = client.delete(f'/api/users/{unique_email}')
    assert response.status_code == 200, f"Expected 200 on delete, got {response.status_code}"

    # Verify the user is deleted
    response = client.get('/api/users')
    users = response.get_json()
    user = next((u for u in users if u["email"] == unique_email), None)
    assert user is None, "User still exists after deletion"


def test_create_order(client):
    """Test that creating an order returns 201 and updates order history."""
    # Register a new user first.
    client.post('/api/users', json={
        "email": "orderuser@example.com",
        "name": "Order User",
        "password": "orderpassword"
    })
    # Create an order for that user.
    response = client.post('/api/orders', json={
        "user_email": "orderuser@example.com",
        "items": [{"furniture_id": 1, "quantity": 2}],
        "total": 500
    })
    assert response.status_code == 201
    order = response.get_json()
    assert "order_id" in order

def test_update_profile(client):
    """Test that updating a user's profile works correctly."""
    # First register a user.
    client.post('/api/users', json={
        "email": "update@example.com",
        "name": "Old Name",
        "password": "updatepass"
    })
    # Update the user's profile.
    response = client.post('/api/users/update@example.com/profile', json={
        "name": "New Name",
        "address": "123 New Address"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "New Name"
    assert data["address"] == "123 New Address"
