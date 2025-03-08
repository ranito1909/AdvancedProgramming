import uuid
import pytest
from app import app

# Fixture for Flask test client
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_get_furniture(client):
    """Ensure GET /api/furniture returns a 200 status code."""
    response = client.get("/api/furniture")
    assert response.status_code == 200

def test_register_and_delete_user(client):
    """
    Register a new user via POST /api/users, confirm the user appears in GET /api/users,
    then delete the user via DELETE /api/users/<email> and verify deletion.
    """
    unique_email = f"test_{uuid.uuid4()}@example.com"
    
    # Register the user.
    response = client.post("/api/users", json={
        "email": unique_email,
        "name": "Test User",
        "password": "password123"
    })
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    # Verify user exists.
    response = client.get("/api/users")
    users = response.get_json()
    assert any(u["email"] == unique_email for u in users), "User not found after registration."
    
    # Delete the user.
    response = client.delete(f"/api/users/{unique_email}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Confirm deletion.
    response = client.get("/api/users")
    users = response.get_json()
    assert not any(u["email"] == unique_email for u in users), "User still exists after deletion."

def test_create_order(client):
    """
    Create a furniture item (via POST /api/inventory), register a user, then create an order via POST /api/orders.
    Verify that the order is created (status code 201 and order_id exists).
    """
    # Create a furniture item.
    inv_response = client.post("/api/inventory", json={
        "id": 1,
        "type": "Chair",
        "name": "Test Chair",
        "description": "A test chair for order creation",
        "price": 75.0,
        "dimensions": [30, 30, 30],
        "quantity": 5,
        "cushion_material": "foam"
    })
    assert inv_response.status_code == 201, f"Furniture creation failed: {inv_response.status_code}"
    furniture_data = inv_response.get_json()
    furniture_id = furniture_data.get("id")
    assert furniture_id is not None, "Furniture id not returned"

    # Register a new user.
    user_email = f"orderuser_{uuid.uuid4()}@example.com"
    user_response = client.post("/api/users", json={
        "email": user_email,
        "name": "Order User",
        "password": "orderpassword"
    })
    assert user_response.status_code == 201, f"User registration failed: {user_response.status_code}"

    # Create an order.
    order_response = client.post("/api/orders", json={
        "user_email": user_email,
        "items": [{"furniture_id": furniture_id, "quantity": 2}]
    })
    assert order_response.status_code == 201, f"Order creation failed: {order_response.status_code}"
    order_data = order_response.get_json()
    assert "order_id" in order_data, "order_id not present in order response"

def test_search(client):
    """
    Create a furniture item (via POST /api/inventory) and then search for it using POST /api/inventorysearch.
    Verify the search returns the expected item.
    """
    # Create a furniture item for searching.
    inv_response = client.post("/api/inventory", json={
        "id": 2,
        "type": "Chair",
        "name": "Search Chair",
        "description": "A chair for search testing",
        "price": 80.0,
        "dimensions": [30, 30, 30],
        "quantity": 3,
        "cushion_material": "foam"
    })
    assert inv_response.status_code == 201

    payload = {
        "name_substring": "Search Chair",
        "min_price": 75.0,
        "max_price": 85.0,
        "furniture_type": "Chair"
    }
    response = client.post("/api/inventorysearch", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list), "Response should be a list"
    assert len(data) >= 1, "Should match at least 1 item"
    result_item = data[0]
    assert result_item["name"] == "Search Chair"
    assert result_item["price"] == 80.0

def test_update_profile(client):
    """
    Register a user and then update their profile via POST /api/users/<email>/profile.
    Verify that the changes persist.
    """
    unique_email = f"update_{uuid.uuid4()}@example.com"
    response = client.post("/api/users", json={
        "email": unique_email,
        "name": "Old Name",
        "password": "updatepass"
    })
    assert response.status_code == 201
    response = client.post(f"/api/users/{unique_email}/profile", json={
        "name": "New Name",
        "address": "123 New Address"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "New Name"
    assert data["address"] == "123 New Address"

def test_update_cart(client):
    """
    Create a furniture item via POST /api/inventory and then update a shopping cart via PUT /api/cart/<email>.
    Verify that the cart reflects the changes.
    """
    email = f"cartupdate_{uuid.uuid4()}@example.com"
    # Create a furniture item.
    inv_response = client.post("/api/inventory", json={
        "id": 3,
        "type": "Chair",
        "name": "Cart Chair",
        "description": "A chair for cart update",
        "price": 100.0,
        "dimensions": [40, 40, 90],
        "quantity": 10,
        "cushion_material": "foam"
    })
    assert inv_response.status_code == 201
    furniture_data = inv_response.get_json()
    furniture_id = furniture_data.get("id")
    # Create initial cart.
    response = client.put(f"/api/cart/{email}", json={
        "items": [{"furniture_id": furniture_id, "quantity": 3}]
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["user_email"] == email
    # Update the cart with new quantity.
    response = client.put(f"/api/cart/{email}", json={
        "items": [{"furniture_id": furniture_id, "quantity": 5, "unit_price": 100.0}]
    })
    assert response.status_code == 200
    data = response.get_json()
    assert any(item["furniture_id"] == furniture_id and item["quantity"] == 5 for item in data["items"])

def test_update_inventory(client):
    """
    Create a furniture item via POST /api/inventory and then update it via PUT /api/inventory/<furniture_id>.
    Verify that the update is reflected.
    """
    inv_response = client.post("/api/inventory", json={
        "id": 4,
        "type": "Table",
        "name": "Test Table",
        "description": "A test table",
        "price": 150.0,
        "dimensions": [50, 50, 30],
        "quantity": 8,
        "frame_material": "wood"
    })
    assert inv_response.status_code == 201
    furniture_data = inv_response.get_json()
    furniture_id = furniture_data.get("id")
    response = client.put(f"/api/inventory/{furniture_id}", json={
        "price": 180.0,
        "name": "Updated Table"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 180.0
    assert data["name"] == "Updated Table"

def test_delete_cart_item(client):
    """
    Create a shopping cart via PUT /api/cart/<email> and then delete an item via DELETE /api/cart/<email>/<item_id>.
    Verify successful deletion.
    """
    email = f"cartdelete_{uuid.uuid4()}@example.com"
    # Create a furniture item.
    inv_response = client.post("/api/inventory", json={
        "id": 5,
        "type": "Chair",
        "name": "Delete Chair",
        "description": "A chair for deletion from cart",
        "price": 85.0,
        "dimensions": [35, 35, 90],
        "quantity": 5,
        "cushion_material": "foam"
    })
    assert inv_response.status_code == 201
    furniture_data = inv_response.get_json()
    furniture_id = furniture_data.get("id")
    # Create a cart.
    response = client.put(f"/api/cart/{email}", json={
        "items": [{"furniture_id": furniture_id, "quantity": 2}]
    })
    assert response.status_code == 200
    # Delete the item from the cart.
    response = client.delete(f"/api/cart/{email}/{furniture_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert "Item removed" in data["message"]

def test_delete_inventory(client):
    """
    Create a furniture item via POST /api/inventory, then delete it via DELETE /api/inventory/<furniture_id>.
    Afterwards, ensure that an update to the deleted item returns 404.
    """
    inv_response = client.post("/api/inventory", json={
        "id": 6,
        "type": "Chair",
        "name": "Delete Inventory Chair",
        "description": "Chair to be deleted",
        "price": 95.0,
        "dimensions": [40, 40, 90],
        "quantity": 1,
        "cushion_material": "foam"
    })

    assert inv_response.status_code == 201
    furniture_data = inv_response.get_json()
    furniture_id = furniture_data.get("id")
    response = client.delete(f"/api/inventory/{furniture_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert "Furniture item deleted" in data["message"]
    # Attempt to update the deleted item.
    response = client.put(f"/api/inventory/{furniture_id}", json={"price": 100.0})
    assert response.status_code == 404

def test_leafitem_discount_within_limits(client):
    """
    Use PUT /api/cart/<email> to add an item with a discount (0<=discount<=100) and verify that
    the discount is applied correctly.
    """
    email = f"discount_{uuid.uuid4()}@example.com"
    # Create a furniture item.
    inv_response = client.post("/api/inventory", json={
        "id": 7,
        "type": "Lamp",
        "name": "Discount Lamp",
        "description": "Lamp for discount test",
        "price": 200.0,
        "dimensions": [20, 20, 40],
        "quantity": 5,
        "light_source": "LED"
    })
    assert inv_response.status_code == 201
    furniture_data = inv_response.get_json()
    furniture_id = furniture_data.get("id")
    # Update cart with a discount of 50%
    response = client.put(f"/api/cart/{email}", json={
        "items": [{"furniture_id": furniture_id, "quantity": 1, "discount": 50, "unit_price": 200.0}]
    })
    assert response.status_code == 200
    data = response.get_json()
    # After a 50% discount, price should be 100.
    assert data["total_price"] == 118.0

def test_leafitem_discount_over_100(client):
    """
    Use PUT /api/cart/<email> to add an item with a discount >100%.
    Expect a 400 error.
    """
    email = f"discount_fail_{uuid.uuid4()}@example.com"
    inv_response = client.post("/api/inventory", json={
        "id": 8,
        "type": "Lamp",
        "name": "OverDiscount Lamp",
        "description": "Lamp for discount failure test",
        "price": 200.0,
        "dimensions": [20, 20, 40],
        "quantity": 5,
        "light_source": "LED"
    })
    assert inv_response.status_code == 201
    furniture_data = inv_response.get_json()
    furniture_id = furniture_data.get("id")
    response = client.put(f"/api/cart/{email}", json={
        "items": [{"furniture_id": furniture_id, "quantity": 1, "discount": 150, "unit_price": 200.0}]
    })
    assert response.status_code == 400

def test_checkout_missing_fields(client):
    """
    Call POST /api/checkout/<email> with missing payment_method and address,
    expecting a 400 response.
    """
    email = f"checkout_missing_{uuid.uuid4()}@example.com"
    # Register user and create an empty cart.
    user_response = client.post("/api/users", json={
        "email": email,
        "name": "Checkout Missing",
        "password": "pass"
    })
    assert user_response.status_code == 201
    cart_response = client.put(f"/api/cart/{email}", json={"items": []})
    assert cart_response.status_code == 200
    response = client.post(f"/api/checkout/{email}", json={})
    assert response.status_code == 400

def test_checkout_no_shopping_cart(client):
    """
    Register a user (via /api/users) without creating a cart, then call checkout.
    Expect a 404 response.
    """
    email = f"checkout_nocart_{uuid.uuid4()}@example.com"
    user_response = client.post("/api/users", json={
        "email": email,
        "name": "No Cart",
        "password": "pass"
    })
    assert user_response.status_code == 201
    response = client.post(f"/api/checkout/{email}", json={
        "payment_method": "credit_card",
        "address": "123 Checkout St"
    })
    assert response.status_code == 404

def test_checkout_no_user(client):
    """
    Create a cart for a user that is not registered, then call checkout.
    Expect a 404 response.
    """
    email = f"checkout_nouser_{uuid.uuid4()}@example.com"
    cart_response = client.put(f"/api/cart/{email}", json={"items": []})
    assert cart_response.status_code == 200
    response = client.post(f"/api/checkout/{email}", json={
        "payment_method": "credit_card",
        "address": "123 Checkout St"
    })
    assert response.status_code == 404

def test_checkout_finalization_failure(client):
    """
    Create a cart with an item that does not correspond to any existing furniture in inventory.
    Expect checkout to fail (400).
    """
    email = f"checkout_fail_{uuid.uuid4()}@example.com"
    user_response = client.post("/api/users", json={
        "email": email,
        "name": "Checkout Fail",
        "password": "pass"
    })
    assert user_response.status_code == 201
    # Add a cart item with a furniture_id that doesn't exist .
    cart_response = client.put(f"/api/cart/{email}", json={
        "items": [{"furniture_id": -1, "quantity": 1, "unit_price": 100.0}]
    })
    assert cart_response.status_code == 200
    response = client.post(f"/api/checkout/{email}", json={
        "payment_method": "credit_card",
        "address": "456 Fail St"
    })
    assert response.status_code == 400

def test_checkout_success(client):
    """
    Create a furniture item via /api/inventory, register a user, create a cart with the item,
    and perform a successful checkout.
    Expect a 200 response and a valid order summary.
    """
    email = f"checkout_success_{uuid.uuid4()}@example.com"
    user_response = client.post("/api/users", json={
        "email": email,
        "name": "Checkout Success",
        "password": "pass"
    })
    assert user_response.status_code == 201
    inv_response = client.post("/api/inventory", json={
        "id": 9,
        "type": "Chair",
        "name": "Success Chair",
        "description": "Chair for checkout success test",
        "price": 150.0,
        "dimensions": [40, 40, 90],
        "quantity": 10,
        "cushion_material": "foam"
    })
    assert inv_response.status_code == 201
    furniture_data = inv_response.get_json()
    furniture_id = furniture_data.get("id")
    cart_response = client.put(f"/api/cart/{email}", json={
        "items": [{"furniture_id": furniture_id, "quantity": 1, "unit_price": 150.0}]
    })
    assert cart_response.status_code == 200
    checkout_response = client.post(f"/api/checkout/{email}", json={
        "payment_method": "credit_card",
        "address": "123 Success Ave"
    })
    assert checkout_response.status_code == 200
    data = checkout_response.get_json()
    assert "Order finalized successfully." in data["message"]
    assert "order_summary" in data

def test_login_success(client):
    # First, register a user
    email = "login_success@example.com"
    password = "mypassword"
    reg_resp = client.post("/api/users", json={
        "email": email,
        "name": "Login Success",
        "password": password,
        "address": "123 Test Blvd"
    })
    assert reg_resp.status_code == 201

    # Then, attempt a successful login
    login_resp = client.post("/api/login", json={
        "email": email,
        "password": password
    })
    assert login_resp.status_code == 200
    data = login_resp.get_json()
    assert data["email"] == email
    assert data["name"] == "Login Success"


def test_login_failure_wrong_credentials(client):
    # Attempt to log in with an unregistered user or wrong password
    login_resp = client.post("/api/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert login_resp.status_code == 401
    data = login_resp.get_json()
    assert "error" in data


def test_set_password_success(client):
    email = f"setpassword@example.com"
    old_password = "oldpassword"
    new_password = "newpassword"
    # Register a new user.
    reg_resp = client.post("/api/users", json={
        "email": email,
        "name": "Test SetPassword User",
        "password": old_password,
        "address": "123 Test St"
    })
    assert reg_resp.status_code == 201

    # Update password using the new endpoint.
    update_resp = client.put(f"/api/users/{email}/password", json={
        "new_password": new_password
    })
    assert update_resp.status_code == 200
    data = update_resp.get_json()
    assert "Password updated successfully" in data["message"]

    # Verify that logging in with the old password fails.
    login_old = client.post("/api/login", json={
        "email": email,
        "password": old_password
    })
    assert login_old.status_code == 401

    # Verify that logging in with the new password succeeds.
    login_new = client.post("/api/login", json={
        "email": email,
        "password": new_password
    })
    assert login_new.status_code == 200

def test_check_password_success(client):
    email = f"checkpass@example.com"
    password = "mypassword"
    # Register the user.
    reg_resp = client.post("/api/users", json={
        "email": email,
        "name": "Test CheckPassword",
        "password": password,
        "address": "123 Test Rd"
    })
    assert reg_resp.status_code == 201

    # Check that the correct password returns True.
    resp = client.post(f"/api/users/{email}/check_password", json={"password": password})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["password_correct"] is True

def test_hash_password(client):
    password = "testpassword"
    
    # First request to hash the password
    response1 = client.post("/api/hash_password", json={"password": password})
    assert response1.status_code == 200
    data1 = response1.get_json()
    assert "hashed_password" in data1

    # Second request to hash the same password to check consistency
    response2 = client.post("/api/hash_password", json={"password": password})
    assert response2.status_code == 200
    data2 = response2.get_json()

    # Verify both hashes are identical
    assert data1["hashed_password"] == data2["hashed_password"]

def test_set_order_status_success(client):
    import uuid

    # Register a user
    email = f"order_status_{uuid.uuid4()}@example.com"
    client.post("/api/users", json={
        "email": email,
        "name": "Order Status User",
        "password": "password"
    })

    # Create a furniture item
    inv_response = client.post("/api/inventory", json={
        "id": 100,
        "type": "Chair",
        "name": "Status Test Chair",
        "description": "Chair for order status test",
        "price": 100.0,
        "dimensions": [40, 40, 90],
        "quantity": 10,
        "cushion_material": "foam"
    })
    assert inv_response.status_code == 201
    furniture_id = inv_response.get_json()["id"]

    # Create an order
    order_response = client.post("/api/orders", json={
        "user_email": email,
        "items": [{"furniture_id": furniture_id, "quantity": 1}]
    })
    assert order_response.status_code == 201
    order_id = order_response.get_json()["order_id"]

    # Update the order status
    update_resp = client.put(f"/api/orders/{order_id}/status", json={"status": "SHIPPED"})
    assert update_resp.status_code == 200
    data = update_resp.get_json()
    assert "Order status updated successfully" in data["message"]

def test_get_order_status_success(client):
    # Register a user
    email = f"getstatus@example.com"
    client.post("/api/users", json={
        "email": email,
        "name": "Get Status User",
        "password": "password"
    })

    # Create a furniture item
    inv_response = client.post("/api/inventory", json={
        "id": 200,
        "type": "Chair",
        "name": "Status Test Chair",
        "description": "Chair for status test",
        "price": 100.0,
        "dimensions": [40, 40, 90],
        "quantity": 10,
        "cushion_material": "foam"
    })
    assert inv_response.status_code == 201
    furniture_id = inv_response.get_json()["id"]

    # Create an order
    order_response = client.post("/api/orders", json={
        "user_email": email,
        "items": [{"furniture_id": furniture_id, "quantity": 1}]
    })
    assert order_response.status_code == 201
    order_id = order_response.get_json()["order_id"]

    # Retrieve the order status
    get_status_resp = client.get(f"/api/orders/{order_id}/status")
    assert get_status_resp.status_code == 200
    data = get_status_resp.get_json()
    assert data["order_id"] == order_id
    assert data["status"] == "PENDING"  # Default status
