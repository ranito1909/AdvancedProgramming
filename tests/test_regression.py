'''import pytest
import app
from Catalog import Checkout, ShoppingCart, User, Inventory, LeafItem

# Helper: clear domain state between tests if needed.
@pytest.fixture(autouse=True)
def clear_domain_state():
    # Clear the Inventory items and User store before each regression test.
    inv = Inventory.get_instance()
    inv.items.clear()
    User._users.clear()
    # Also clear global DataFrames if necessary (orders_df, cart_df)
    app.orders_df = app.orders_df.iloc[0:0]
    app.cart_df = app.cart_df.iloc[0:0]
    app.furniture_df = app.furniture_df.iloc[0:0]
    yield

# Regression Test: Furniture Creation and Retrieval
def test_furniture_creation_and_retrieval(client):
    """
    Process:
      1. Create a new furniture item (Chair) via POST /api/inventory.
      2. Retrieve the furniture list using GET /api/furniture.
      3. Verify the returned JSON and also that the Inventory instance holds the new item.
    """
    response = client.post(
        "/api/inventory",
        json={
            "type": "Chair",
            "name": "Reg Test Chair",
            "description": "Chair for furniture retrieval regression test",
            "price": 120.0,
            "dimensions": [40, 40, 90],
            "quantity": 5,
            "cushion_material": "memory foam"
        }
    )
    assert response.status_code == 201, f"Furniture creation failed: {response.status_code}"
    furniture_data = response.get_json()
    fid = furniture_data.get("id")
    assert fid is not None, "Furniture id not returned"

    # Call GET /api/furniture endpoint
    response = client.get("/api/furniture")
    assert response.status_code == 200, "Failed to retrieve furniture list"
    items = response.get_json()
    found = any(item["name"] == "Reg Test Chair" for item in items)
    assert found, "Created furniture not found in API retrieval"

    # Additionally, check the Inventory instance directly
    inv = Inventory.get_instance()
    found_in_inv = any(getattr(item, "id", None) == fid for item in inv.items.keys())
    assert found_in_inv, "Created furniture not found in Inventory instance"

# Regression Test: User Registration and Profile Update
def test_user_registration_and_profile_update(client):
    """
    Process:
      1. Register a new user via POST /api/users.
      2. Update the user's profile via POST /api/users/<email>/profile.
      3. Retrieve the user (via GET /api/users) and check the underlying User instance.
    """
    unique_email = f"reguser_{pytest.uuid4() if hasattr(pytest, 'uuid4') else 'unique'}@example.com"
    response = client.post(
        "/api/users",
        json={
            "email": unique_email,
            "name": "Initial Name",
            "password": "testpass"
        }
    )
    assert response.status_code == 201, "User registration failed"
    # Verify that the User domain instance is updated.
    user_instance = User.get_user(unique_email)
    assert user_instance is not None, "User instance not created in domain model"
    assert user_instance.name == "Initial Name", "Initial name not set correctly"
    
    # Update the profile
    response = client.post(
        f"/api/users/{unique_email}/profile",
        json={"name": "Updated Name", "address": "123 Regression Ave"}
    )
    assert response.status_code == 200, "Profile update failed"
    updated_user = response.get_json()
    assert updated_user["name"] == "Updated Name", "Name update not applied"
    assert updated_user["address"] == "123 Regression Ave", "Address update not applied"
    
    # Check underlying instance again
    user_instance = User.get_user(unique_email)
    assert user_instance.name == "Updated Name", "Domain instance name not updated"
    assert user_instance.address == "123 Regression Ave", "Domain instance address not updated"

# Regression Test: Order Creation and User Order History Update
def test_order_creation_and_user_history(client):
    """
    Regression Test: Order Creation and User Order History Update
    Process:
      1. Create a furniture item (Chair) via POST /api/inventory.
      2. Register a user via POST /api/users.
      3. Create an order via POST /api/orders referencing the created furniture.
      4. Retrieve the user via GET /api/users and verify that the User instance’s order_history is updated.
    """
    # Create furniture item and capture its id
    response = client.post(
        "/api/inventory",
        json={
            "type": "Chair",
            "name": "Order Test Chair",
            "description": "Chair for order regression test",
            "price": 90.0,
            "dimensions": [35, 35, 85],
            "quantity": 8,
            "cushion_material": "fabric"
        }
    )
    assert response.status_code == 201, "Furniture creation for order test failed"
    furniture_data = response.get_json()
    fid = furniture_data.get("id")
    assert fid is not None, "Furniture id not returned"
    
    # Register user
    email = "order_regression@example.com"
    response = client.post(
        "/api/users",
        json={
            "email": email,
            "name": "Order Regression User",
            "password": "orderpass"
        }
    )
    assert response.status_code == 201, "User registration for order test failed"
    
    # Create order referencing the captured furniture id
    response = client.post(
        "/api/orders",
        json={
            "user_email": email,
            "items": [{"furniture_id": fid, "quantity": 2}]
        }
    )
    assert response.status_code == 201, "Order creation failed"
    
    # Verify user's order history via the API and domain model
    response = client.get("/api/users")
    users = response.get_json()
    user = next((u for u in users if u["email"] == email), None)
    assert user is not None, "User not found after order creation"
    assert len(user["order_history"]) > 0, "Order history not updated after order creation"

# Regression Test: Shopping Cart Update and Deletion
def test_cart_update_and_deletion(client):
    """
    Process:
      1. Create a shopping cart for a user via PUT /api/cart/<email> with initial items.
      2. Update the cart with new items.
      3. Delete a specific cart item via DELETE /api/cart/<email>/<item_id>.
      4. Verify via the API response that the cart contents are updated.
    """
    email = "cart_regression@example.com"
    # Create initial cart with two items
    response = client.put(
        f"/api/cart/{email}",
        json={"items": [{"furniture_id": 101, "quantity": 2}, {"furniture_id": 202, "quantity": 1}]}
    )
    assert response.status_code == 200, "Initial cart creation failed"
    
    # Update the cart with new items
    response = client.put(
        f"/api/cart/{email}",
        json={"items": [{"furniture_id": 101, "quantity": 3}, {"furniture_id": 303, "quantity": 2}]}
    )
    assert response.status_code == 200, "Cart update failed"
    data = response.get_json()
    assert any(item["furniture_id"] == 101 and item["quantity"] == 3 for item in data["items"]), \
        "Cart update did not reflect new quantity for furniture_id 101"
    
    # Delete a cart item (furniture_id 101)
    response = client.delete(f"/api/cart/{email}/101")
    assert response.status_code == 200, "Cart item deletion failed"
    data = response.get_json()
    assert not any(item["furniture_id"] == 101 for item in data.get("items", [])), \
        "Cart item 101 still exists after deletion"

# Regression Test: Inventory Update and Deletion
def test_inventory_update_and_deletion(client):
    """
    Process:
      1. Create a dummy furniture item via POST /api/inventory.
      2. Update the item via PUT /api/inventory/<id>.
      3. Delete the item via DELETE /api/inventory/<id>.
      4. Verify via the API and domain instance that further updates fail.
    """
    # Create dummy furniture item (Chair)
    response = client.post(
        "/api/inventory",
        json={
            "type": "Chair",
            "name": "Inventory Test Chair",
            "description": "Chair for inventory regression test",
            "price": 80.0,
            "dimensions": [40, 40, 90],
            "quantity": 3,
            "cushion_material": "gel"
        }
    )
    assert response.status_code == 201, "Inventory test furniture creation failed"
    furniture_data = response.get_json()
    fid = furniture_data["id"]
    
    # Update the item via API
    response = client.put(f"/api/inventory/{fid}", json={"price": 85.0, "name": "Updated Inventory Chair"})
    assert response.status_code == 200, "Inventory update failed"
    updated_data = response.get_json()
    assert updated_data["price"] == 85.0, "Price not updated correctly"
    assert updated_data["name"] == "Updated Inventory Chair", "Name not updated correctly"
    
    # Delete the item via API
    response = client.delete(f"/api/inventory/{fid}")
    assert response.status_code == 200, "Inventory deletion failed"
    
    # Attempt to update the deleted item, expecting 404
    response = client.put(f"/api/inventory/{fid}", json={"price": 90.0})
    assert response.status_code == 404, "Updating a deleted inventory item should return 404"

# Regression Test: Complete Checkout Process Integration
def test_checkout_process_regression(client):
    """
    Process:
      1. Create a furniture item (Chair) via POST /api/inventory.
      2. Register a new user via POST /api/users.
      3. Simulate a shopping cart by adding a LeafItem via the API (using domain logic) for the furniture.
      4. Use the Checkout process (via domain instance) to finalize the order.
      5. Verify via API (and domain instance) that the inventory quantity decreases and the user's order history is updated.
    """
    # Create furniture item
    response = client.post(
        "/api/inventory",
        json={
            "type": "Chair",
            "name": "Checkout Test Chair",
            "description": "Chair for checkout regression test",
            "price": 150.0,
            "dimensions": [50, 50, 100],
            "quantity": 5,
            "cushion_material": "leather"
        }
    )
    assert response.status_code == 201, "Checkout test furniture creation failed"
    furniture_data = response.get_json()
    fid = furniture_data["id"]

    # Register user
    email = "checkout_regression@example.com"
    response = client.post(
        "/api/users",
        json={
            "email": email,
            "name": "Checkout Regression User",
            "password": "checkoutpass"
        }
    )
    assert response.status_code == 201, "User registration for checkout failed"

    # Verify that the user instance exists in the domain model
    user = User.get_user(email)
    assert user is not None, "User not found in domain model for checkout test"

    # Use the domain Inventory instance to find the created furniture
    inventory_instance = Inventory.get_instance()
    furniture_item = next((item for item in inventory_instance.items.keys() if getattr(item, "id", None) == fid), None)
    assert furniture_item is not None, "Furniture item not found in Inventory for checkout test"

    # Create a shopping cart and add a LeafItem for the furniture (simulate API behavior)
    cart = ShoppingCart()
    cart.add_item(LeafItem(furniture_item.name, furniture_item.price, quantity=1))
    
    # Create a Checkout instance and finalize order
    checkout = Checkout(user, cart, inventory_instance)
    checkout.set_payment_method("Credit Card")
    checkout.set_address("456 Checkout Street")
    result = checkout.finalize_order()
    assert result is True, "Checkout finalization failed"

    # Verify that the Inventory instance quantity decreased (initially 5, now 4)
    new_qty = inventory_instance.get_quantity(furniture_item)
    assert new_qty == 4, f"Expected inventory quantity 4 after checkout, got {new_qty}"

    # Verify that the User instance's order_history is updated
    assert len(user.order_history) > 0, "User's order history not updated after checkout"

# Regression Test: Discount Application in Checkout Process
def test_discount_application_in_checkout_regression(client):
    """
    Process:
      1. Create a furniture item (Chair) via POST /api/inventory.
      2. Register a user via POST /api/users.
      3. Create a shopping cart by adding a LeafItem for the furniture with quantity 2.
      4. Apply a discount (25%) to the LeafItem.
      5. Finalize checkout via domain Checkout instance.
      6. Verify that the final total price reflects the discount and that inventory updates correctly.
    """
    # Create furniture item
    response = client.post(
        "/api/inventory",
        json={
            "type": "Chair",
            "name": "Discount Test Chair",
            "description": "Chair for discount application regression test",
            "price": 200.0,
            "dimensions": [45, 45, 95],
            "quantity": 10,
            "cushion_material": "suede"
        }
    )
    assert response.status_code == 201, "Discount test furniture creation failed"
    furniture_data = response.get_json()
    fid = furniture_data["id"]

    # Register user
    email = "discount_regression@example.com"
    response = client.post(
        "/api/users",
        json={
            "email": email,
            "name": "Discount Regression User",
            "password": "discountpass"
        }
    )
    assert response.status_code == 201, "User registration for discount test failed"

    # Retrieve the domain Inventory and the created furniture item
    inventory_instance = Inventory.get_instance()
    furniture_item = next((item for item in inventory_instance.items.keys() if getattr(item, "id", None) == fid), None)
    assert furniture_item is not None, "Furniture item not found in Inventory for discount test"

    # Create a shopping cart and add a LeafItem (quantity 2) for the furniture
    cart = ShoppingCart()
    leaf_item = LeafItem(furniture_item.name, furniture_item.price, quantity=2)
    # Apply a 25% discount on the LeafItem
    leaf_item.apply_discount(25)
    cart.add_item(leaf_item)
    
    # Retrieve the user from the domain model and create a Checkout instance
    user = User.get_user(email)
    assert user is not None, "User not found in domain model for discount checkout test"

    checkout = Checkout(user, cart, inventory_instance)
    checkout.set_payment_method("PayPal")
    checkout.set_address("789 Discount Blvd")
    result = checkout.finalize_order()
    assert result is True, "Checkout with discount failed"
    
    # Expected total: 200 with 25% discount -> 150 per unit; 2 units => 300
    expected_total = 300.0
    actual_total = cart.get_total_price()
    assert abs(actual_total - expected_total) < 0.01, f"Expected total {expected_total}, got {actual_total}"
    
    # Verify Inventory update: initial quantity 10, purchased 2, so expected quantity 8
    new_qty = inventory_instance.get_quantity(furniture_item)
    assert new_qty == 8, f"Expected inventory quantity 8 after discount checkout, got {new_qty}"'''


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
    {"type": "Chair", "name": "Test Chair", "price": 120.0, "quantity": 5},
    {"type": "Table", "name": "Test Table", "price": 250.0, "quantity": 3}
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
    response = client.post("/api/orders", json={"user_email": "invalid@example.com", "items": []})
    assert response.status_code == 400, "Order should fail when items are empty"

def test_invalid_cart_update(client):
    response = client.put("/api/cart/invalid@example.com", json={"items": [{"furniture_id": 9999, "quantity": 1}]})
    assert response.status_code == 400, "Cart update should fail for non-existent furniture"

def test_authentication_required(client):
    response = client.get("/api/users/protected-resource")  # Assuming protected endpoint
    assert response.status_code == 401, "Authentication required test failed"

@pytest.mark.parametrize("discount_data", [
    {"furniture_id": 101, "quantity": 2, "discount": 10},
    {"furniture_id": 202, "quantity": 1, "discount": 20}
])
def test_discount_application(client, discount_data):
    email = "discount@example.com"
    response = client.put(f"/api/cart/{email}", json={"items": [discount_data]})
    assert response.status_code == 200

    response = client.post(f"/api/checkout/{email}", json={"payment_method": "PayPal", "address": "789 Discount Blvd"})
    assert response.status_code == 200


