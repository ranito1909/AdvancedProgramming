import pytest
import app
from Catalog import Checkout, ShoppingCart, User, Inventory, LeafItem, Chair

# Regression Test: Furniture Creation and Retrieval
def test_furniture_creation_and_retrieval(client):
    """
    Regression Test: Furniture Creation and Retrieval
    Process:
      1. Create a new furniture item (Chair) using POST /api/inventory.
      2. Retrieve the furniture list using GET /api/furniture.
      3. Verify that the created furniture appears in the retrieved list.
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
    
    # Retrieve furniture list and verify the new item exists
    response = client.get("/api/furniture")
    assert response.status_code == 200, "Failed to retrieve furniture list"
    items = response.get_json()
    found = any(item["name"] == "Reg Test Chair" for item in items)
    assert found, "Created furniture not found in inventory retrieval"

# Regression Test: User Registration and Profile Update
def test_user_registration_and_profile_update(client):
    """
    Regression Test: User Registration and Profile Update
    Process:
      1. Register a new user via POST /api/users.
      2. Update the user's profile (name and address) via POST /api/users/<email>/profile.
      3. Retrieve the user and verify that profile changes are persisted.
    """
    unique_email = f"reguser_{pytest.uuid4() if hasattr(pytest, 'uuid4') else 'unique'}@example.com"
    # Register the user
    response = client.post(
        "/api/users",
        json={
            "email": unique_email,
            "name": "Initial Name",
            "password": "testpass"
        }
    )
    assert response.status_code == 201, "User registration failed"
    
    # Update the user profile
    response = client.post(
        f"/api/users/{unique_email}/profile",
        json={"name": "Updated Name", "address": "123 Regression Ave"}
    )
    assert response.status_code == 200, "Profile update failed"
    updated_user = response.get_json()
    assert updated_user["name"] == "Updated Name", "Name update not applied"
    assert updated_user["address"] == "123 Regression Ave", "Address update not applied"

# Regression Test: Order Creation and User Order History Update
def test_order_creation_and_user_history(client):
    """
    Regression Test: Order Creation and User Order History Update
    Process:
      1. Create a furniture item (Chair) via POST /api/inventory.
      2. Register a user via POST /api/users.
      3. Create an order via POST /api/orders referencing the created furniture.
      4. Retrieve the user via GET /api/users and verify the order_history includes the new order.
    """
    # Create furniture item
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
    
    # Create order (assuming the furniture is assigned id 1)
    response = client.post(
        "/api/orders",
        json={
            "user_email": email,
            "items": [{"furniture_id": 1, "quantity": 2}]
        }
    )
    assert response.status_code == 201, "Order creation failed"
    
    # Verify user's order history
    response = client.get("/api/users")
    users = response.get_json()
    user = next((u for u in users if u["email"] == email), None)
    assert user is not None, "User not found after order creation"
    assert len(user["order_history"]) > 0, "Order history not updated after order creation"

# Regression Test: Shopping Cart Update and Deletion
def test_cart_update_and_deletion(client):
    """
    Regression Test: Shopping Cart Update and Deletion
    Process:
      1. Create a shopping cart for a user via PUT /api/cart/<email> with initial items.
      2. Update the cart with new items.
      3. Delete a specific cart item via DELETE /api/cart/<email>/<item_id>.
      4. Verify that the cart contents reflect these operations.
    """
    email = "cart_regression@example.com"

    # Pre-populate the inventory with dummy items matching the test furniture IDs.
    # We use the concrete Chair class (adjust parameters as needed).
    dummy_item_101 = app.Chair("Item101", "Test item 101", 50.0, (40, 40, 40), "foam")
    dummy_item_101.id = 101
    app.inventory.items[dummy_item_101] = 10

    dummy_item_202 = app.Chair("Item202", "Test item 202", 75.0, (40, 40, 40), "foam")
    dummy_item_202.id = 202
    app.inventory.items[dummy_item_202] = 5

    dummy_item_303 = app.Chair("Item303", "Test item 303", 100.0, (40, 40, 40), "foam")
    dummy_item_303.id = 303
    app.inventory.items[dummy_item_303] = 20

    # Create initial cart with two items
    response = client.put(
        f"/api/cart/{email}",
        json={"items": [{"furniture_id": 101, "quantity": 2}, {"furniture_id": 202, "quantity": 1}]}
    )
    assert response.status_code == 200, "Initial cart creation failed"
    
    # Update the cart with new items (change quantity for id 101 and add a new item id 303)
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
    Regression Test: Inventory Update and Deletion
    Process:
      1. Create a dummy furniture item via POST /api/inventory.
      2. Update the furniture item via PUT /api/inventory/<id>.
      3. Delete the furniture item via DELETE /api/inventory/<id>.
      4. Verify that subsequent update attempts fail (return 404).
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
    
    # Update the item
    response = client.put(f"/api/inventory/{fid}", json={"price": 85.0, "name": "Updated Inventory Chair"})
    assert response.status_code == 200, "Inventory update failed"
    updated_data = response.get_json()
    assert updated_data["price"] == 85.0, "Price not updated correctly"
    assert updated_data["name"] == "Updated Inventory Chair", "Name not updated correctly"
    
    # Delete the item
    response = client.delete(f"/api/inventory/{fid}")
    assert response.status_code == 200, "Inventory deletion failed"
    
    # Attempt to update the deleted item, expecting 404
    response = client.put(f"/api/inventory/{fid}", json={"price": 90.0})
    assert response.status_code == 404, "Updating a deleted inventory item should return 404"

# Regression Test: Complete Checkout Process Integration
def test_checkout_process_regression(client):
    """
    Regression Test: Complete Checkout Process Integration
    Process:
      1. Create a furniture item (Chair) via POST /api/inventory.
      2. Register a new user via POST /api/users.
      3. Simulate a shopping cart by creating a ShoppingCart and adding a LeafItem for the furniture.
      4. Create a Checkout instance, set payment method and address, and finalize the order.
      5. Verify that the inventory quantity decreases and the user's order history is updated.
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

    # Use Catalog classes for checkout simulation
    inventory_instance = Inventory.get_instance()
    # Locate the created furniture item using its id
    furniture_item = next((item for item in inventory_instance.items.keys() if getattr(item, "id", None) == fid), None)
    assert furniture_item is not None, "Furniture item not found in inventory for checkout test"

    # Create a shopping cart and add one unit of the furniture
    cart = ShoppingCart()
    cart.add_item(LeafItem(furniture_item.name, furniture_item.price, quantity=1))
    
    # Retrieve the user and create a Checkout instance
    user = User.get_user(email)
    assert user is not None, "User not found for checkout test"

    checkout = Checkout(user, cart, inventory_instance)
    checkout.set_payment_method("Credit Card")
    checkout.set_address("456 Checkout Street")

    # Finalize checkout and verify success
    result = checkout.finalize_order()
    assert result is True, "Checkout finalization failed"

    # Verify inventory quantity decreased (initially 5, now should be 4)
    new_qty = inventory_instance.get_quantity(furniture_item)
    assert new_qty == 4, f"Expected inventory quantity 4 after checkout, got {new_qty}"

    # Verify user's order history updated
    assert len(user.order_history) > 0, "User's order history was not updated after checkout"

# Regression Test: Discount Application in Checkout Process
def test_discount_application_in_checkout_regression(client):
    """
    Regression Test: Discount Application in Cart and Checkout
    Process:
      1. Create a furniture item (Chair) via POST /api/inventory.
      2. Register a user via POST /api/users.
      3. Create a shopping cart, add a LeafItem for the furniture with quantity 2.
      4. Apply a discount (25%) to the LeafItem.
      5. Finalize checkout using the Checkout process.
      6. Verify that the final total price reflects the discount and that the inventory updates correctly.
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

    # Use Catalog classes to simulate checkout with discount
    inventory_instance = Inventory.get_instance()
    furniture_item = next((item for item in inventory_instance.items.keys() if getattr(item, "id", None) == fid), None)
    assert furniture_item is not None, "Furniture item not found for discount test"

    # Create a shopping cart and add the furniture as a LeafItem with quantity 2
    cart = ShoppingCart()
    leaf_item = LeafItem(furniture_item.name, furniture_item.price, quantity=2)
    # Apply a 25% discount on the LeafItem
    leaf_item.apply_discount(25)
    cart.add_item(leaf_item)
    
    # Retrieve the user and create a Checkout instance
    user = User.get_user(email)
    assert user is not None, "User not found for discount checkout test"

    checkout = Checkout(user, cart, inventory_instance)
    checkout.set_payment_method("PayPal")
    checkout.set_address("789 Discount Blvd")
    
    # Finalize checkout
    result = checkout.finalize_order()
    assert result is True, "Checkout with discount failed"
    
    # Expected price: Original price 200, 25% discount -> 150 per unit, quantity 2 -> total 300
    expected_total = 300.0
    actual_total = cart.get_total_price()
    assert abs(actual_total - expected_total) < 0.01, f"Expected total {expected_total}, got {actual_total}"
    
    # Verify inventory update: initial quantity 10, purchased 2, expected quantity 8
    new_qty = inventory_instance.get_quantity(furniture_item)
    assert new_qty == 8, f"Expected inventory quantity 8 after discount checkout, got {new_qty}"

    
