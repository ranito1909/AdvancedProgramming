import pytest
import app

@pytest.fixture(autouse=True)
def clear_domain_state():
    # Clear the Inventory items and User store before each regression test.
    inv = app.Inventory.get_instance()
    inv.items.clear()
    app.User._users.clear()
    app.orders_df = app.orders_df.iloc[0:0]
    app.cart_df = app.cart_df.iloc[0:0]
    app.furniture_df = app.furniture_df.iloc[0:0]
    yield

@pytest.mark.parametrize("furniture_data", [
    {"type": "Chair", "name": "Test Chair", "price": 120.0, "quantity": 5, "cushion_material": "foam"},
    {"type": "Table", "name": "Test Table", "price": 250.0, "quantity": 3, "frame_material": "wood"}
])
def test_furniture_creation_and_retrieval(client, furniture_data):
    response = client.post("/api/inventory", json=furniture_data)
    assert response.status_code == 201
    fid = response.get_json()["id"]

    response = client.get("/api/furniture")
    assert response.status_code == 200
    assert any(item["id"] == fid for item in response.get_json())

@pytest.mark.parametrize("user_data", [
    {"email": "user1@example.com", "name": "User One", "password": "pass1"},
    {"email": "user2@example.com", "name": "User Two", "password": "pass2"}
])
def test_user_registration_and_profile_update(client, user_data):
    response = client.post("/api/users", json=user_data)
    assert response.status_code == 201

    profile_update = {"name": "Updated Name", "address": "123 Regression Ave"}
    response = client.post(f"/api/users/{user_data['email']}/profile", json=profile_update)
    assert response.status_code == 200
    updated_user = response.get_json()
    assert updated_user["name"] == "Updated Name"
    assert updated_user["address"] == "123 Regression Ave"

def test_invalid_order_creation(client):
    # Register a valid user.
    client.post("/api/users", json={
        "email": "valid@example.com",
        "name": "Valid User",
        "password": "pass"
    })
    response = client.post("/api/orders", json={"user_email": "valid@example.com", "items": []})
    assert response.status_code == 400, "Order should fail when items are empty"

def test_invalid_cart_update(client):
    response = client.put("/api/cart/invalid@example.com", json={"items": [{"furniture_id": 9999, "quantity": 1}]})
    assert response.status_code == 404, "Cart update should fail for non-existent furniture"


def test_discount_application(client):
    # First, register the user for discount application.
    client.post("/api/users", json={
        "email": "discount@example.com",
        "name": "Discount User",
        "password": "discountpass"
    })

    # Create an inventory item first.
    inv_response = client.post("/api/inventory", json={
        "type": "Chair",
        "name": "Discount Chair",
        "description": "Discount test chair",
        "price": 100.0,
        "dimensions": [40, 40, 90],
        "quantity": 10,
        "cushion_material": "foam"
    })
    discount_item = inv_response.get_json()
    discount_id = discount_item["id"]

    discount_data = {"furniture_id": discount_id, "quantity": 2, "discount": 10}
    email = "discount@example.com"
    response = client.put(f"/api/cart/{email}", json={"items": [discount_data]})
    assert response.status_code == 200

    response = client.post(f"/api/checkout/{email}", json={
        "payment_method": "PayPal",
        "address": "789 Discount Blvd"
    })
    assert response.status_code == 200
