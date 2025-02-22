# tests/regresstion.py
def test_order_updates_user_history(client):
    # Register a new user
    client.post(
        "/api/users",
        json={
            "email": "regression@example.com",
            "name": "Regression Test",
            "password": "regress123",
        },
    )
    # Create an order for this user
    client.post(
        "/api/orders",
        json={
            "user_email": "regression@example.com",
            "items": [{"furniture_id": 1, "quantity": 1}],
            "total": 100,
        },
    )
    # Verify that the order history was updated
    response = client.get("/api/users")
    users = response.get_json()
    user = next((u for u in users if u["email"] == "regression@example.com"), None)
    assert user is not None
    assert len(user["order_history"]) > 0

# tests/test_regression.py

def test_order_updates_user_history(client):
    """
    1) Register a user
    2) Create an order for that user
    3) GET /api/users => confirm user_history has at least 1 entry
    """
    # Register user
    client.post(
        "/api/users",
        json={
            "email": "regression@example.com",
            "name": "Regression Test",
            "password": "regress123",
        },
    )

    # Create order
    client.post(
        "/api/orders",
        json={
            "user_email": "regression@example.com",
            "items": [{"furniture_id": 1, "quantity": 1}],
            "total": 100,
        },
    )

    # Check the user's order history
    response = client.get("/api/users")
    users = response.get_json()
    user = next((u for u in users if u["email"] == "regression@example.com"), None)
    assert user is not None, "User not found after registration"
    assert len(user["order_history"]) > 0, "Expected order_history to have 1+ entries"

def test_full_checkout_flow(client):
    """
    Full checkout flow test:
    1) Register a new user
    2) Add an item to the user's cart
    3) Perform checkout
    4) Verify inventory update after purchase
    """
    user_email = "checkout@example.com"

    # Register a user
    client.post("/api/users", json={"email": user_email, "name": "Checkout User", "password": "pass123"})

    # Add a chair to the cart
    client.put(f"/api/cart/{user_email}", json={"items": [{"furniture_id": 1, "quantity": 1}]})

    # Perform checkout
    response = client.post("/api/checkout", json={"user_email": user_email})
    assert response.status_code == 201
    order_data = response.get_json()
    assert "order_id" in order_data