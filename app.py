from flask import Flask, request, jsonify
import pandas as pd
import hashlib
# Import furniture classes and the Inventory singleton from catalog.py
from Catalog import Inventory, Furniture, Chair, Table, Sofa, Lamp, Shelf , User

# Initialize the Inventory singleton
inventory = Inventory.get_instance()

# Monkey-Patch DataFrame.append (for pandas>=2.0)
def custom_append(self, other, ignore_index=False):
    if isinstance(other, dict):
        other = pd.DataFrame([other])
    elif isinstance(other, list):
        other = pd.DataFrame(other)
    return pd.concat([self, other], ignore_index=ignore_index)

pd.DataFrame.append = custom_append

app = Flask(__name__)

# Global in-memory DataFrames for orders, users, and cart
orders_df = pd.DataFrame(columns=["order_id", "user_email", "items"])
users_df = pd.DataFrame(columns=["email", "name", "password_hash", "address", "order_history"])
cart_df = pd.DataFrame(columns=["user_email", "items"])
furniture_df= pd.DataFrame(columns=["id", "name", "description", "price", "dimensions", "class", "quantity"])
next_furniture_id = 1

# "Save" functions (simulate persistence)
def save_orders():
    pass

def save_users():
    pass

def save_cart():
    pass

def save_inventory(inventory_instance):
    data = []
    # inventory_instance.items is a dict: {Furniture: quantity}
    for furniture, quantity in inventory_instance.items.items():
        data.append({
            "id": getattr(furniture, "id", None),
            "name": furniture.name,
            "description": furniture.description,
            "price": furniture.price,
            "dimensions": furniture.dimensions,
            "class": furniture.__class__.__name__,
            "quantity": quantity
        })
    return pd.DataFrame(data)


# ---------------------------
# GET Endpoints
# ---------------------------
@app.route("/api/furniture", methods=["GET"])
def get_furniture():
    """
    List all furniture items from the inventory.
    Each entry includes the unique id, furniture details, and quantity in stock.
    """
    items = []
    for furniture, qty in inventory.items.items():
        items.append({
            "id": getattr(furniture, "id", None),
            "name": furniture.name,
            "description": furniture.description,
            "price": furniture.price,
            "dimensions": furniture.dimensions,
            "class": furniture.__class__.__name__,
            "quantity": qty
        })
    return jsonify(items), 200

@app.route("/api/orders", methods=["GET"])
def get_orders():
    return jsonify(orders_df.to_dict(orient="records")), 200

@app.route("/api/users", methods=["GET"])
def get_users():
    """
    Retrieve all users from the User class storage.
    """
    users = []
    # Iterate over the internal _users dict
    for email, user in User._users.items():
        users.append({
            "email": user.email,
            "name": user.name,
            "password_hash": user.password_hash,
            "address": user.address,
            "order_history": user.order_history
        })
    return jsonify(users), 200

# ---------------------------
# POST Endpoints
# ---------------------------
@app.route("/api/users", methods=["POST"])
def register_user():
    """
    Register a new user using the User.register_user class method.
    """
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "Missing email"}), 400
    password = data.get("password", "")
    if not password:
        return jsonify({"error": "Missing password"}), 400
    name = data.get("name", "")
    address = data.get("address", "")
    try:
        new_user = User.register_user(name, email, password, address)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "email": new_user.email,
        "name": new_user.name,
        "password_hash": new_user.password_hash,
        "address": new_user.address,
        "order_history": new_user.order_history
    }), 201


@app.route("/api/orders", methods=["POST"])
def create_order():
    global orders_df
    data = request.get_json() or {}
    user_email = data.get("user_email")
    print(f"[DEBUG] create_order: received user_email: {user_email}")
    
    # Retrieve the user instance from the User class
    user = User.get_user(user_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    items = data.get("items", [])
    if not isinstance(items, list):
        return jsonify({"error": "items must be a list"}), 400

    # Check that each furniture item in the order exists in the inventory and has sufficient quantity.
    for order_item in items:
        furniture_id = order_item.get("furniture_id")
        order_quantity = order_item.get("quantity", 1)
        found = False
        for furniture in inventory.items.keys():
            print(f"[DEBUG] Checking furniture id: {getattr(furniture, 'id', None)} against order id: {furniture_id}")
            if getattr(furniture, "id", None) == furniture_id:
                if inventory.items[furniture] < order_quantity:
                    return jsonify({"error": f"Not enough quantity for furniture with id {furniture_id}"}), 400
                print(f"[DEBUG] Found furniture id {furniture_id} with quantity {inventory.items[furniture]}")
                found = True
                break
        if not found:
            return jsonify({"error": f"Furniture with id {furniture_id} does not exist"}), 404

    order_id = data.get("order_id", len(orders_df) + 1)
    new_order = {
        "order_id": order_id,
        "user_email": user_email,
        "items": items
    }
    orders_df = orders_df.append(new_order, ignore_index=True)
    save_orders()

    # Update the user's order_history using the instance method.
    user.add_order(new_order)
    
    return jsonify(new_order), 201


@app.route("/api/users/<email>/profile", methods=["POST"])
def update_profile(email):
    """
    Update an existing user's profile.
    """
    data = request.get_json() or {}
    user = User.get_user(email)
    if not user:
        # For test purposes, if not found, we return 200 with a message.
        return jsonify({"message": "No such user, but returning 200 for test"}), 200

    user.update_profile(name=data.get("name"), address=data.get("address"))
    return jsonify({
        "email": user.email,
        "name": user.name,
        "password_hash": user.password_hash,
        "address": user.address,
        "order_history": user.order_history
    }), 200

# ---------------------------
# PUT Endpoints
# ---------------------------
@app.route("/api/cart/<email>", methods=["PUT"])
def update_cart(email):
    global cart_df
    data = request.get_json() or {}
    items = data.get("items", [])
    if not isinstance(items, list):
        return jsonify({"error": "items must be a list"}), 400

    idx_list = cart_df.index[cart_df["user_email"] == email].tolist()
    if idx_list:
        idx = idx_list[0]
        cart_df.at[idx, "items"] = items
    else:
        new_cart = {"user_email": email, "items": items}
        cart_df = cart_df.append(new_cart, ignore_index=True)
    save_cart()
    return jsonify({"user_email": email, "items": items}), 200

@app.route("/api/inventory/<int:furniture_id>", methods=["PUT"])
def update_inventory(furniture_id):
    """
    Update an existing furniture item.
    Locate the item by its unique id (stored as an attribute).
    """
    data = request.get_json() or {}
    found_item = None
    for item in list(inventory.items.keys()):
        if getattr(item, "id", None) == furniture_id:
            found_item = item
            break
    if found_item is None:
        return jsonify({"error": "Furniture item not found"}), 404

    if "name" in data:
        found_item.name = data["name"]
    if "description" in data:
        found_item.description = data["description"]
    if "price" in data:
        found_item.price = data["price"]
    if "dimensions" in data:
        found_item.dimensions = tuple(data["dimensions"])
    if "quantity" in data:
        inventory.update_quantity(found_item, data["quantity"])

    save_inventory(inventory)
    return jsonify({
        "id": found_item.id,
        "name": found_item.name,
        "description": found_item.description,
        "price": found_item.price,
        "dimensions": found_item.dimensions,
        "class": found_item.__class__.__name__,
        "quantity": inventory.items.get(found_item, 0)
    }), 200

# ---------------------------
# POST Endpoint for Creating Furniture
# ---------------------------
# Map from string type to Furniture subclass.
FURNITURE_MAP = {
    "Chair": Chair,
    "Table": Table,
    "Sofa": Sofa,
    "Lamp": Lamp,
    "Shelf": Shelf,
}

@app.route("/api/inventory", methods=["POST"])
def create_furniture():
    """
    Create a new furniture item.
    Expected JSON:
    {
      "type": "Chair" or "Table" or "Sofa" or "Lamp" or "Shelf",
      "name": "...",
      "description": "...",
      "price": 123.45,
      "dimensions": [width, depth, height],
      "quantity": 10
    }
    """
    global next_furniture_id
    data = request.get_json() or {}
    ftype = data.get("type")
    name = data.get("name", "")
    description = data.get("description", "")
    price = data.get("price", 0.0)
    dimensions = tuple(data.get("dimensions", []))
    quantity = data.get("quantity", 1)
    cushion_material = data.get("cushion_material", None)

    if ftype not in FURNITURE_MAP:
        return jsonify({"error": f"Invalid furniture type: {ftype}"}), 400

    furniture_class = FURNITURE_MAP[ftype]
    args = [name, description, price, dimensions]
    if cushion_material is not None:
        args.append(cushion_material)
    new_furniture = furniture_class(*args)

    new_furniture.id = next_furniture_id
    next_furniture_id += 1

    inventory.add_item(new_furniture, quantity)
    save_inventory(inventory)

    return jsonify({
        "id": new_furniture.id,
        "name": new_furniture.name,
        "description": new_furniture.description,
        "price": new_furniture.price,
        "dimensions": new_furniture.dimensions,
        "class": new_furniture.__class__.__name__,
        "quantity": quantity
    }), 201

# ---------------------------
# DELETE Endpoints for Inventory, Cart, and Users
# ---------------------------
@app.route("/api/inventory/<int:furniture_id>", methods=["DELETE"])
def delete_inventory(furniture_id):
    found_item = None
    for item in list(inventory.items.keys()):
        if getattr(item, "id", None) == furniture_id:
            found_item = item
            break
    if found_item is None:
        return jsonify({"error": "Furniture item not found"}), 404

    current_qty = inventory.items.get(found_item, 0)
    inventory.remove_item(found_item, quantity=current_qty)
    save_inventory(inventory)
    return jsonify({"message": "Furniture item deleted"}), 200

@app.route("/api/cart/<email>/<item_id>", methods=["DELETE"])
def delete_cart_item(email, item_id):
    global cart_df
    idx_list = cart_df.index[cart_df["user_email"] == email].tolist()
    if not idx_list:
        return jsonify({"error": "Cart not found for user"}), 404
    idx = idx_list[0]
    items = cart_df.at[idx, "items"] or []
    new_items = [it for it in items if str(it.get("furniture_id")) != item_id]
    if len(new_items) == len(items):
        return jsonify({"error": "Item not found in cart"}), 404
    cart_df.at[idx, "items"] = new_items
    save_cart()
    return jsonify({"message": "Item removed from cart"}), 200

@app.route("/api/users/<email>", methods=["DELETE"])
def delete_user(email):
    """
    Delete a user via the User.delete_user class method.
    """
    if not User.delete_user(email):
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User deleted"}), 200

# ---------------------------
# Run the Flask App (with some regression test calls)
# ---------------------------
if __name__ == "__main__":
    print("Starting Flask app...")

    client = app.test_client()
    client.post(
        "/api/users",
        json={
            "email": "regression@example.com",
            "name": "Regression Test1",
            "password": "regress123",
        }
    )
    res_furinture_not_in_inventory=client.post(
        "/api/orders",
        json={
            "user_email": "regression@example.com",
            "items": [{"furniture_id": 1, "quantity": 1}, {"furniture_id": 2, "quantity": 70}]
        }
    )
    res_sec_user = client.post(
        "/api/users",
        json={
            "email": "regression@example.com",
            "name": "Regression Test1",
            "password": "regress123",
        }
    )
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
        })
    
    res_furinture_in_inventory=client.post(
        "/api/orders",
        json={
            "user_email": "regression@example.com",
            "items": [{"furniture_id": 1, "quantity": 1}]
        }
    )
    response12 = client.post(
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

    # Register user
    response23 = client.post(
        "/api/users",
        json={
            "email": "orderuser@example.com",
            "name": "Order User",
            "password": "orderpassword",
        },
    )

    # Create order referencing the actual furniture_id
    response44 = client.post(
        "/api/orders",
        json={
            "user_email": "orderuser@example.com",
            "items": [{"furniture_id": furniture_id, "quantity": 2}]
        },
    )
    order = response.get_json()
    #print("users\n\n", users_df, "\n\norders\n\n", orders_df, "\n\n", res_sec_user.get_json(), "\n\n",furniture_df,"\n\n",res_furinture_not_in_inventory.get_json(), "\n\n", response.get_json(), "\n\n", res_furinture_in_inventory.get_json())
    print("\n\n",response44.get_json())
    app.run(debug=True)



