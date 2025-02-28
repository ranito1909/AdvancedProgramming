def test_order_updates_user_history(client):
    """
    1) Create a furniture item (a Chair) in the inventory.
    2) Register a user.
    3) Create an order for that user referencing the furniture.
    4) GET /api/users => confirm order_history has at least 1 entry.
    """
    # Create a furniture item. Note: for a Chair, we require a cushion_material.
    response = client.post(
        "/api/inventory",
        json={
            "type": "Chair",
            "name": "Regression Chair",
            "description": "A chair for regression test",
            "price": 100.0,
            "dimensions": [40, 40, 90],
            "quantity": 10,
            "cushion_material": "foam"
        },
    )
    assert response.status_code == 201, f"Expected furniture creation to return 201, got {response.status_code}"

    # Register user
    response = client.post(
        "/api/users",
        json={
            "email": "regression@example.com",
            "name": "Regression Test",
            "password": "regress123",
        },
    )
    assert response.status_code == 201, f"User registration failed with {response.status_code}"

    # Create order referencing the furniture id (assumed to be 1)
    response = client.post(
        "/api/orders",
        json={
            "user_email": "regression@example.com",
            "items": [{"furniture_id": 1, "quantity": 1}]
        },
    )
    assert response.status_code == 201, f"Order creation failed with {response.status_code}"

    # Check the user's order history
    response = client.get("/api/users")
    users = response.get_json()
    user = next((u for u in users if u["email"] == "regression@example.com"), None)
    assert user is not None, "User not found after registration"
    assert len(user["order_history"]) > 0, "Expected order_history to have 1+ entries"
