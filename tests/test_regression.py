# tests/regresstion.py
def test_order_updates_user_history(client):
    # Register a new user
    client.post('/api/users', json={
        "email": "regression@example.com",
        "name": "Regression Test",
        "password": "regress123"
    })

    # Create an order for this user
    client.post('/api/orders', json={
        "user_email": "regression@example.com",
        "items": [{"furniture_id": 1, "quantity": 1}],
        "total": 100
    })

    # Verify that the order history was updated
    response = client.get('/api/users')
    users = response.get_json()
    user = next((u for u in users if u["email"] == "regression@example.com"), None)
    assert user is not None
    assert len(user['order_history']) > 0
