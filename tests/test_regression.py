import pytest
import app
import pandas as pd

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
    {"id": 1, "name": "Test Chair", "description": "Red chair", "price": 100.0, "dimensions": [40, 40, 90], "type": "Chair", "quantity": 5, "cushion_material": "foam"},
    {"id": 2, "name": "Test Table", "description": "Blue table", "price": 250.0, "dimensions": [50, 50, 100], "type": "Table", "quantity": 3, "frame_material": "wood"},

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
        "id": 3,
        "name": "Discount Chair",
        "description": "Discount test chair",
        "price": 100.0, 
        "dimensions": [40, 40, 90], 
        "type": "Chair", 
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

def test_create_furniture_persistence(client):
    """
    Test that when create_furniture is called, the inventory persistence file is updated.
    """
    # Send POST request to create a new furniture item.
    response = client.post(
        "/api/inventory",
        json={
            "type": "Chair",
            "name": "Automated Test Chair",
            "description": "A chair created during automated testing",
            "price": 85.0,
            "dimensions": [35, 35, 90],
            "quantity": 7,
            "cushion_material": "memory foam"
        }
    )
    # Assert that the response indicates success.
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    # Now, simulate a 'restart' by loading the persisted inventory file.
    inventory_df = pd.read_pickle("storage/inventory.pkl")

    # Verify that the DataFrame contains the new furniture item.
    # For example, check that the new item is in the DataFrame by name.
    new_item = inventory_df[inventory_df["name"] == "Automated Test Chair"]
    assert not new_item.empty, "Automated Test Chair not found in the persisted inventory."

@pytest.mark.regression
def test_full_regression_flow(client):
    """
    A regression test that exercises the entire flow:
        1. User registration
        2. Creating orders with valid and invalid inventory
        3. Adding inventory
        4. Updating shopping cart
        5. Removing items from cart
        6. Checking out
    """
    # --- User Registration for Regression Testing ---
    reg_user_response = client.post(
        "/api/users",
        json={
            "email": "regression@example.com",
            "name": "Regression Test1",
            "password": "regress123",
        }
    )
    assert reg_user_response.status_code == 201, "User registration should succeed."

    # --- Place an Order with Items Not in Inventory ---
    res_furniture_not_in_inventory = client.post(
        "/api/orders",
        json={
            "user_email": "regression@example.com",
            "items": [{"furniture_id": 1, "quantity": 1}, {"furniture_id": 2, "quantity": 70}]
        }
    )
    # Example check (you can refine or remove as needed):
    assert res_furniture_not_in_inventory.status_code in (400, 404), \
        "An order with items not in inventory should fail."

    # --- Second User Registration (Regression) ---
    sec_user_response = client.post(
        "/api/users",
        json={
            "email": "regression@example.com",
            "name": "Regression Test1",
            "password": "regress123",
        }
    )
    # Possibly expect a 409 or 400 if user already exists

    # --- Add Inventory: Regression Chair ---
    inv_response = client.post(
        "/api/inventory",
        json={
            "id": 1,
            "type": "Chair",
            "name": "Regression Chair",
            "description": "A chair for regression test",
            "price": 100.0,
            "dimensions": [40, 40, 90],
            "quantity": 10,
            "cushion_material": "foam"
        }
    )
    assert inv_response.status_code == 201, "Should successfully add regression chair to inventory."

    # --- Place Order for an Item That Is in Inventory ---
    res_furniture_in_inventory = client.post(
        "/api/orders",
        json={
            "user_email": "regression@example.com",
            "items": [{"furniture_id": 1039, "quantity": 1}]
        }
    )
    assert res_furniture_in_inventory.status_code == 201, "Valid order with existing item should succeed."

    # --- Add Inventory: Test Chair ---
    test_chair_response = client.post(
        "/api/inventory",
        json={
            "type": "Chair",
            "name": "Test Chair",
            "description": "A test chair for order creation",
            "price": 75.0,
            "dimensions": [30, 30, 30],
            "quantity": 5,
            "cushion_material": "foam"
        }
    )
    assert test_chair_response.status_code == 201, "Furniture creation failed."
    furniture_data = test_chair_response.get_json()
    furniture_id = furniture_data.get("id")

    # --- Register Order User ---
    order_user_response = client.post(
        "/api/users",
        json={
            "email": "orderuser@example.com",
            "name": "Order User",
            "password": "orderpassword",
        }
    )
    assert order_user_response.status_code == 201, "Order user registration should succeed."

    # --- Create Order for Order User Using the Actual Furniture ID ---
    order_response = client.post(
        "/api/orders",
        json={
            "user_email": "orderuser@example.com",
            "items": [{"furniture_id": furniture_id, "quantity": 2}]
        }
    )
    assert order_response.status_code == 201, "Order creation for existing user/furniture should succeed."

    # --- Register User for Cart Update and Checkout ---
    cart_update_user_response = client.post(
        "/api/users",
        json={
            "email": "cartupdate@example.com",
            "name": "Cart Update User",
            "password": "cartpassword"
        }
    )
    assert cart_update_user_response.status_code == 201, "Cart update user registration should succeed."

    # --- Search Inventory (for Chairs) ---
    search_response = client.post(
        "/api/inventorysearch",
        json={
            "name_substring": "Chair",
            "min_price": 50.0,
            "max_price": 100.0,
            "furniture_type": "Chair"
        }
    )
    assert search_response.status_code == 200, "Inventory search should succeed."

    # --- Add Inventory Item for Cart Update User Checkout ---
    inventory_cart_response = client.post(
        "/api/inventory",
        json={
            "type": "Sofa",
            "name": "CartUpdate Sofa",
            "description": "A sofa for cart update checkout test",
            "price": 300.0,
            "dimensions": [200, 90, 100],
            "quantity": 5,
            "cushion_material": "leather"
        }
    )
    inventory_cart_data = inventory_cart_response.get_json()
    furniture_id_cartupdate = inventory_cart_data.get("id")
    assert inventory_cart_response.status_code == 201, "Should successfully add Sofa to inventory."

    # --- Update Shopping Cart for cartupdate@example.com ---
    cart_response_initial = client.put(
        "/api/cart/cartupdate@example.com",
        json={"items": [{"furniture_id": furniture_id_cartupdate, "quantity": 3}]}
    )
    assert cart_response_initial.status_code == 200, "Initial cart update should succeed."

    cart_response_updated = client.put(
        "/api/cart/cartupdate@example.com",
        json={"items": [{"furniture_id": furniture_id_cartupdate, "quantity": 5}]}
    )
    assert cart_response_updated.status_code == 200, "Cart update with new quantity should succeed."

    # Another cart update with explicit unit_price
    cart_response_initial = client.put(
        "/api/cart/cartupdate@example.com",
        json={
            "items": [
                {
                    "furniture_id": furniture_id_cartupdate,
                    "quantity": 3,
                    "unit_price": 100.0
                }
            ]
        }
    )
    assert cart_response_initial.status_code == 200, "Cart update with explicit unit_price should succeed."

    cart_response_updated = client.put(
        "/api/cart/cartupdate@example.com",
        json={
            "items": [
                {
                    "furniture_id": furniture_id_cartupdate,
                    "quantity": 5,
                    "unit_price": 300.0
                }
            ]
        }
    )
    assert cart_response_updated.status_code == 200, "Cart update with changed unit_price should succeed."

    # --- Remove Item from Cart for cartupdate@example.com ---
    remove_item_response = client.post(
        "/api/cart/cartupdate@example.com/remove",
        json={
            "item_id": furniture_id_cartupdate,
            "unit_price": 300.0,
            "quantity": 3
        }
    )
    assert remove_item_response.status_code == 200, "Removing item from cart should succeed."

    # --- Checkout Process for cartupdate@example.com ---
    checkout_payload = {"payment_method": "credit_card", "address": "123 Test St"}
    checkout_response = client.post("/api/checkout/cartupdate@example.com", json=checkout_payload)
    assert checkout_response.status_code == 201, "Checkout should succeed after valid cart update."

    # --- Retrieve and Print All Orders ---
    orders_response = client.get("/api/orders")

    assert orders_response.status_code == 200, "Retrieving all orders should succeed."
