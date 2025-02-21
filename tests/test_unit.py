# tests/unit.py
import uuid
import app


def test_get_furniture(client):
    response = client.get("/api/furniture")
    assert response.status_code == 200


def test_register_and_delete_user(client):
    # Generate a unique email for the test
    unique_email = f"test_{uuid.uuid4()}@example.com"

    # Register the user with the unique email
    response = client.post(
        "/api/users",
        json={"email": unique_email, "name": "Test User", "password": "password123"},
    )
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    # Optionally verify the user is in the list
    response = client.get("/api/users")
    users = response.get_json()
    user = next((u for u in users if u["email"] == unique_email), None)
    assert user is not None, "User was not found after registration"

    # Delete the user
    response = client.delete(f"/api/users/{unique_email}")
    assert (
        response.status_code == 200
    ), f"Expected 200 on delete, got {response.status_code}"

    # Verify the user is deleted
    response = client.get("/api/users")
    users = response.get_json()
    user = next((u for u in users if u["email"] == unique_email), None)
    assert user is None, "User still exists after deletion"


def test_create_order(client):
    """Test that creating an order returns 201 and updates order history."""
    # Register a new user first.
    client.post(
        "/api/users",
        json={
            "email": "orderuser@example.com",
            "name": "Order User",
            "password": "orderpassword",
        },
    )
    # Create an order for that user.
    response = client.post(
        "/api/orders",
        json={
            "user_email": "orderuser@example.com",
            "items": [{"furniture_id": 1, "quantity": 2}],
            "total": 500,
        },
    )
    assert response.status_code == 201
    order = response.get_json()
    assert "order_id" in order


def test_update_profile(client):
    """Test that updating a user's profile works correctly."""
    # First register a user.
    client.post(
        "/api/users",
        json={
            "email": "update@example.com",
            "name": "Old Name",
            "password": "updatepass",
        },
    )
    # Update the user's profile.
    response = client.post(
        "/api/users/update@example.com/profile",
        json={"name": "New Name", "address": "123 New Address"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "New Name"
    assert data["address"] == "123 New Address"


def test_update_cart(client):
    """Test that updating the cart for a user works correctly."""
    email = "cartupdate@example.com"

    # Create a new cart for the user.
    response = client.put(
        f"/api/cart/{email}", json={"items": [{"furniture_id": 10, "quantity": 3}]}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["user_email"] == email
    assert data["items"] == [{"furniture_id": 10, "quantity": 3}]

    # Update the cart for the same user.
    response = client.put(
        f"/api/cart/{email}",
        json={
            "items": [
                {"furniture_id": 10, "quantity": 5},
                {"furniture_id": 20, "quantity": 1},
            ]
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["items"] == [
        {"furniture_id": 10, "quantity": 5},
        {"furniture_id": 20, "quantity": 1},
    ]


def test_update_inventory(client):
    """Test that updating a furniture item works correctly."""
    # Add a dummy furniture item directly to the global DataFrame.
    # (Assuming the test environment allows manipulation of app.furniture_df)
    app.furniture_df = app.furniture_df.append(
        {
            "id": 999,
            "name": "Test Table",
            "description": "A test table",
            "price": 100.0,
            "dimensions": (50, 50, 30),
        },
        ignore_index=True,
    )
    app.save_furniture()

    # Update the furniture item.
    response = client.put(
        "/api/inventory/999", json={"price": 120.0, "name": "Updated Test Table"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 120.0
    assert data["name"] == "Updated Test Table"


def test_delete_cart_item(client):
    """Test deleting a specific item from the user's cart."""
    email = "cartdelete@example.com"
    cart_items = [
        {"furniture_id": 101, "quantity": 2},
        {"furniture_id": 202, "quantity": 1},
    ]
    # Create the cart
    response = client.put(f"/api/cart/{email}", json={"items": cart_items})
    assert response.status_code == 200

    # Delete one item (furniture_id 101)
    response = client.delete(f"/api/cart/{email}/101")
    assert response.status_code == 200
    data = response.get_json()
    assert "Item removed" in data["message"]

    # Try deleting an item that doesn't exist; expect a 404.
    response = client.delete(f"/api/cart/{email}/999")
    assert response.status_code == 404


def test_delete_inventory(client):
    """Test that deleting a furniture item works correctly."""
    # Add a dummy furniture item to be deleted.
    app.furniture_df = app.furniture_df.append(
        {
            "id": 888,
            "name": "Delete Chair",
            "description": "Chair to be deleted",
            "price": 75.0,
            "dimensions": (40, 40, 90),
        },
        ignore_index=True,
    )
    app.save_furniture()

    # Delete the furniture item.
    response = client.delete("/api/inventory/888")
    assert response.status_code == 200
    data = response.get_json()
    assert "Furniture item deleted" in data["message"]

    # Verify deletion by attempting an update (which should fail).
    response = client.put("/api/inventory/888", json={"price": 80.0})
    assert response.status_code == 404
