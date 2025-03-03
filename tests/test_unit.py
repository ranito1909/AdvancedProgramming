# tests/test_unit.py
import uuid
import pytest
import app
from Catalog import LeafItem, Table, Chair, Furniture


def test_get_furniture(client):
    """
    Ensure the GET /api/furniture endpoint returns a 200 status code.
    """
    response = client.get("/api/furniture")
    assert response.status_code == 200


def test_register_and_delete_user(client):
    """
    1) Register a new user with a unique email
    2) Verify the user is in /api/users
    3) Delete that user
    4) Verify deletion in /api/users
    """
    unique_email = f"test_{uuid.uuid4()}@example.com"

    # Register the user
    response = client.post(
        "/api/users",
        json={"email": unique_email, "name": "Test User", "password": "password123"},
    )
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    # Check user appears
    response = client.get("/api/users")
    users = response.get_json()
    user = next((u for u in users if u["email"] == unique_email), None)
    assert user is not None, "User was not found after registration"

    # Delete the user
    response = client.delete(f"/api/users/{unique_email}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Ensure user is gone
    response = client.get("/api/users")
    users = response.get_json()
    user = next((u for u in users if u["email"] == unique_email), None)
    assert user is None, "User still exists after deletion"


def test_create_order(client):
    """
    1) Create a furniture item so it exists in inventory.
    2) Register a new user.
    3) Create an order for that user via POST /api/orders.
    4) Ensure status code 201 and that order_id is in the returned JSON.
    """
    # Create a furniture item and capture its id
    response = client.post(
        "/api/inventory",
        json={
            "type": "Chair",
            "name": "Test Chair",
            "description": "A test chair for order creation",
            "price": 75.0,
            "dimensions": [30, 30, 30],
            "quantity": 5,
            "cushion_material": "foam"
        },
    )
    assert response.status_code == 201, f"Furniture creation failed: {response.status_code}"
    furniture_data = response.get_json()
    furniture_id = furniture_data.get("id")
    assert furniture_id is not None, "Furniture id not returned"

    # Register user
    response = client.post(
        "/api/users",
        json={
            "email": "orderuser@example.com",
            "name": "Order User",
            "password": "orderpassword",
        },
    )
    assert response.status_code == 201, f"User registration failed: {response.status_code}"

    # Create order referencing the actual furniture_id
    response = client.post(
        "/api/orders",
        json={
            "user_email": "orderuser@example.com",
            "items": [{"furniture_id": furniture_id, "quantity": 2}]
        },
    )
    assert response.status_code == 201, f"Order creation failed: {response.status_code}"
    order = response.get_json()
    assert "order_id" in order, "order_id not present in order response"



def test_update_profile(client):
    """
    1) Register a user.
    2) POST /api/users/<email>/profile to update name and address.
    3) Verify changes persisted.
    """
    client.post(
        "/api/users",
        json={
            "email": "update@example.com",
            "name": "Old Name",
            "password": "updatepass",
        },
    )

    response = client.post(
        "/api/users/update@example.com/profile",
        json={"name": "New Name", "address": "123 New Address"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "New Name"
    assert data["address"] == "123 New Address"


def test_update_cart(client):
    """
    1) PUT /api/cart/<email> to create a cart with items.
    2) PUT again to update the items.
    3) Verify both operations succeed with status_code 200.
    """
    email = "cartupdate@example.com"
    dummy_item = app.Chair("Dummy Chair", "For testing", 100.0, (30, 30, 30), "foam")
    dummy_item.id = 10
    app.inventory.items[dummy_item] = 10

    # Initial cart
    response = client.put(
        f"/api/cart/{email}", json={"items": [{"furniture_id": 10, "quantity": 3}]}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["user_email"] == email
    assert data["items"] == [{"furniture_id": 10, "quantity": 3}]

    # Update cart
    response = client.put(
        f"/api/cart/{email}",
        json={"items": [{"furniture_id": 10, "quantity": 5}]},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["items"] == [
        {"furniture_id": 10, "quantity": 5}
    ]


def test_update_inventory(client):
    """
    1) Add a dummy furniture item directly to the Inventory singleton.
    2) Call save_inventory to update furniture_df.
    3) PUT /api/inventory/<id> to update the item.
    4) Ensure changes are reflected in the response.
    """
    # Create a dummy Table item; supply required parameter "wood" for frame_material.
    dummy = Table("Test Table", "A test table", 100.0, (50, 50, 30), "wood")
    dummy.id = 999
    app.inventory.add_item(dummy, 10)
    app.furniture_df = app.save_inventory(app.inventory)

    # Update the item
    response = client.put("/api/inventory/999", json={"price": 120.0, "name": "Updated Test Table"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 120.0
    assert data["name"] == "Updated Test Table"


def test_delete_cart_item(client):
    """
    1) Create a cart with two items.
    2) DELETE one item => expect 200.
    3) DELETE a non-existing item => expect 404.
    """
    email = "cartdelete@example.com"
    cart_items = [{"furniture_id": 10, "quantity": 2}]
    # Create the cart
    response = client.put(f"/api/cart/{email}", json={"items": cart_items})
    assert response.status_code == 200

    # Delete one item
    response = client.delete(f"/api/cart/{email}/10")
    assert response.status_code == 200
    data = response.get_json()
    assert "Item removed" in data["message"]

    # Attempt to delete nonexistent item => 404
    response = client.delete(f"/api/cart/{email}/999")
    assert response.status_code == 404


def test_delete_inventory(client):
    """
    1) Add a dummy furniture item directly to the Inventory singleton.
    2) Call save_inventory to update furniture_df.
    3) DELETE that item => expect 200.
    4) Try updating it => expect 404.
    """
    # Create a dummy Chair item; supply required parameter "foam" for cushion_material.
    dummy = Chair("Delete Chair", "Chair to be deleted", 75.0, (40, 40, 90), "foam")
    dummy.id = 888
    app.inventory.add_item(dummy, 1)
    app.furniture_df = app.save_inventory(app.inventory)

    # Delete the item
    response = client.delete("/api/inventory/888")
    assert response.status_code == 200
    data = response.get_json()
    assert "Furniture item deleted" in data["message"]

    # Attempt to update the deleted item
    response = client.put("/api/inventory/888", json={"price": 80.0})
    assert response.status_code == 404


#
# NEW TESTS FOR DISCOUNT ENFORCEMENT
#
def test_leafitem_discount_within_limits():
    """
    Create a LeafItem and apply various discounts between 0% and 100%.
    Verify that the new price is correct, and no exceptions are raised.
    """
    item = LeafItem("Test Lamp", 200.0, quantity=1)

    # 0% discount => price stays the same
    item.apply_discount(0)
    assert item.get_price() == 200.0

    # 50% discount => price halves
    item.apply_discount(50)
    assert item.get_price() == 100.0

    # 100% discount => price is 0
    item.apply_discount(100)
    assert item.get_price() == 0.0


def test_leafitem_discount_over_100():
    """
    Attempt to apply a discount > 100%.
    Expect a ValueError to be raised (enforced in LeafItem.apply_discount).
    """
    item = LeafItem("Test Chair", 100.0, quantity=1)
    with pytest.raises(ValueError):
        item.apply_discount(150)  # 150% discount => not allowed


def test_checkout_missing_fields(client):
    """
    Test /api/checkout/<email> with missing payment_method and address.
    Expected to return 400.
    """
    email = "checkout_missing@example.com"
    # Setup: register user and create a shopping cart.
    user = app.User("Test Checkout Missing", email, "dummyhash")
    app.User._users[email] = user
    cart = app.ShoppingCart()
    app.shopping_carts[email] = cart

    # Do not provide payment_method or address.
    response = client.post(f"/api/checkout/{email}", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "Both payment_method and address are required." in data["error"]

def test_checkout_no_shopping_cart(client):
    """
    Test /api/checkout/<email> when there is no shopping cart.
    Expected to return 404.
    """
    email = "checkout_nocart@example.com"
    # Setup: create user but do not create a shopping cart.
    user = app.User("Test No Cart", email, "dummyhash")
    app.User._users[email] = user

    response = client.post(
        f"/api/checkout/{email}",
        json={"payment_method": "credit_card", "address": "123 Checkout St"}
    )
    assert response.status_code == 404
    data = response.get_json()
    assert "Shopping cart not found for user." in data["error"]

def test_checkout_no_user(client):
    """
    Test /api/checkout/<email> when the user is not registered.
    Expected to return 404.
    """
    email = "checkout_nouser@example.com"
    # Setup: create a shopping cart without registering the user.
    cart = app.ShoppingCart()
    app.shopping_carts[email] = cart

    response = client.post(
        f"/api/checkout/{email}",
        json={"payment_method": "credit_card", "address": "123 Checkout St"}
    )
    assert response.status_code == 404
    data = response.get_json()
    assert "User not found." in data["error"]

def test_checkout_finalization_failure(client):
    """
    Test /api/checkout/<email> where order finalization fails.
    Simulated by adding a LeafItem with a name that does not match any furniture in inventory.
    Expected to return 400.
    """
    email = "checkout_fail@example.com"
    user = app.User("Test Checkout Fail", email, "dummyhash")
    app.User._users[email] = user
    cart = app.ShoppingCart()
    # Create a LeafItem referencing non-existent furniture.
    leaf_item = LeafItem("NonExistentFurniture", 100.0, quantity=1)
    cart.add_item(leaf_item)
    app.shopping_carts[email] = cart

    response = client.post(
        f"/api/checkout/{email}",
        json={"payment_method": "credit_card", "address": "456 Fail St"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "Checkout process failed" in data["error"]

def test_checkout_success(client):
    """
    Test a successful checkout:
      - Create a furniture item (Chair) and add it to the inventory.
      - Register a user and create a shopping cart.
      - Add a LeafItem referencing the furniture.
      - Expect a 200 response and a valid order summary.
    """
    email = "checkout_success@example.com"
    user = app.User("Test Checkout Success", email, "dummyhash")
    app.User._users[email] = user
    cart = app.ShoppingCart()
    app.shopping_carts[email] = cart

    # Create a concrete furniture item using the Chair class.
    # Adjust parameters as required by your Chair implementation.
    furniture_item = app.Chair("Test Furniture", "A test chair", 150.0, (50, 50, 100), "foam")
    furniture_item.id = 555  # Manually assign an id for testing.
    app.inventory.items[furniture_item] = 10  # Set available quantity.

    # Add a LeafItem referencing the furniture.
    # The Checkout endpoint will try to find the matching furniture
    # by comparing the LeafItem name (here, the chair's name) with inventory.
    leaf_item = app.LeafItem(furniture_item.name, furniture_item.price, quantity=1)
    cart.add_item(leaf_item)

    response = client.post(
        f"/api/checkout/{email}",
        json={"payment_method": "credit_card", "address": "123 Success Ave"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "Order finalized successfully." in data["message"]
    assert "order_summary" in data
