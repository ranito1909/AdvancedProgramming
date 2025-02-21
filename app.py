from flask import Flask, request, jsonify
import os
import pickle
import pandas as pd

# Import everything you need from your Catalog module
from Catalog import (
    Inventory,
    Chair,
    Table,
    Sofa,
    Lamp,
    Shelf,
    User,
    Order,
    OrderStatus,
    LeafItem,
    CompositeItem,
    ShoppingCart,
    Checkout
)

app = Flask(__name__)

# Persistence file paths
INVENTORY_PICKLE = "inventory.pkl"
USERS_PICKLE = "users.pkl"

# Global orders list for demonstration
orders = []

# Global shopping carts: mapping user email -> ShoppingCart instance
shopping_carts = {}

# ---------------------------
# Helper functions for data persistence and DataFrame creation
# ---------------------------
def load_inventory():
    if os.path.exists(INVENTORY_PICKLE):
        with open(INVENTORY_PICKLE, "rb") as f:
            loaded_items = pickle.load(f)  # Expected: dict of furniture -> quantity
        inv = Inventory.get_instance()
        inv.items = loaded_items
    else:
        Inventory.get_instance()  # Create singleton if not exists

def save_inventory():
    inv = Inventory.get_instance()
    with open(INVENTORY_PICKLE, "wb") as f:
        pickle.dump(inv.items, f)
    # Update the DataFrame attribute for testing purposes
    app.furniture_df = create_furniture_df()

def load_users():
    if os.path.exists(USERS_PICKLE):
        with open(USERS_PICKLE, "rb") as f:
            user_dict = pickle.load(f)
        # Ensure we have a dict (and not None)
        User._users = user_dict if user_dict is not None else {}
    else:
        User._users = {}

def save_users():
    with open(USERS_PICKLE, "wb") as f:
        pickle.dump(User._users, f)

def create_furniture_df():
    inv = Inventory.get_instance()
    data = []
    for furniture_obj, qty in inv.items.items():
        data.append({
            "name": furniture_obj.name,
            "type": type(furniture_obj).__name__,
            "description": furniture_obj.description,
            "price": furniture_obj.price,
            "dimensions": furniture_obj.dimensions,
            "quantity": qty,
        })
    return pd.DataFrame(data)

# ---------------------------
# Initialization (simulate before_first_request)
# ---------------------------
@app.before_request
def initialize_data():
    if not hasattr(app, 'initialized'):
        load_inventory()
        load_users()
        app.furniture_df = create_furniture_df()
        app.initialized = True

# ---------------------------
# INVENTORY / FURNITURE ROUTES
# ---------------------------
@app.route("/api/furniture", methods=["GET"])
def get_furniture():
    inv = Inventory.get_instance()
    response = []
    for furniture_obj, qty in inv.items.items():
        response.append({
            "name": furniture_obj.name,
            "type": type(furniture_obj).__name__,
            "description": furniture_obj.description,
            "price": furniture_obj.price,
            "dimensions": furniture_obj.dimensions,
            "quantity": qty,
        })
    return jsonify(response), 200

@app.route("/api/furniture", methods=["POST"])
def add_furniture():
    data = request.get_json()
    ftype = data.get("type")
    name = data.get("name")
    desc = data.get("description", "")
    price = float(data.get("price", 0))
    dims = tuple(data.get("dimensions", []))
    qty = int(data.get("quantity", 1))
    extra = data.get("extra_attr", "")
    
    if ftype == "Chair":
        furniture_obj = Chair(name, desc, price, dims, cushion_material=extra)
    elif ftype == "Table":
        furniture_obj = Table(name, desc, price, dims, frame_material=extra)
    elif ftype == "Sofa":
        capacity = int(extra) if extra else 3
        furniture_obj = Sofa(name, desc, price, dims, capacity)
    elif ftype == "Lamp":
        furniture_obj = Lamp(name, desc, price, dims, light_source=extra)
    elif ftype == "Shelf":
        wall_mounted = (str(extra).lower() == "true")
        furniture_obj = Shelf(name, desc, price, dims, wall_mounted)
    else:
        return jsonify({"error": "Unsupported furniture type"}), 400

    inv = Inventory.get_instance()
    inv.add_item(furniture_obj, quantity=qty)
    save_inventory()
    return jsonify({"message": f"{ftype} '{name}' added with quantity {qty}"}), 201

@app.route("/api/furniture/<string:name>", methods=["PUT"])
def update_furniture(name):
    data = request.get_json()
    inv = Inventory.get_instance()
    furniture_obj = None
    for fobj in inv.items.keys():
        if fobj.name == name:
            furniture_obj = fobj
            break
    if not furniture_obj:
        return jsonify({"error": "Furniture not found"}), 404

    new_price = data.get("price")
    new_desc = data.get("description")
    new_qty = data.get("quantity")
    if new_price is not None:
        furniture_obj.price = float(new_price)
    if new_desc is not None:
        furniture_obj.description = new_desc
    if new_qty is not None:
        success = inv.update_quantity(furniture_obj, int(new_qty))
        if not success:
            return jsonify({"error": "Failed to update quantity"}), 400

    save_inventory()
    return jsonify({"message": f"Furniture '{name}' updated successfully"}), 200

@app.route("/api/furniture/<string:name>", methods=["DELETE"])
def delete_furniture(name):
    inv = Inventory.get_instance()
    furniture_obj = None
    for fobj in list(inv.items.keys()):
        if fobj.name == name:
            furniture_obj = fobj
            break
    if not furniture_obj:
        return jsonify({"error": "Furniture not found"}), 404

    inv.remove_item(furniture_obj, quantity=inv.items[furniture_obj])
    save_inventory()
    return jsonify({"message": f"Furniture '{name}' removed from inventory"}), 200

# ---------------------------
# USER ROUTES
# ---------------------------
@app.route("/api/users", methods=["GET"])
def get_users():
    all_users = []
    users_dict = User._users if User._users is not None else {}
    for user in users_dict.values():
        all_users.append({
            "email": user.email,
            "name": user.name,
            "address": user.address,
            "order_history": user.order_history if user.order_history is not None else [],
        })
    return jsonify(all_users), 200

@app.route("/api/users", methods=["POST"])
def register_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    address = data.get("address", "")
    if not (name and email and password):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        user = User.register_user(name, email, password, address=address)
        # Ensure order_history is initialized
        if user.order_history is None:
            user.order_history = []
        save_users()
        # Also create an empty shopping cart for this user
        shopping_carts[email] = ShoppingCart()
        return jsonify({"message": f"User '{email}' registered successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = User.login_user(email, password)
    if user:
        return jsonify({"message": f"Welcome, {user.name}!"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/users/<string:email>", methods=["PUT"])
def update_user(email):
    data = request.get_json()
    user = User.get_user(email)
    if not user:
        return jsonify({"error": "User not found"}), 404
    name = data.get("name")
    address = data.get("address")
    user.update_profile(name=name, address=address)
    save_users()
    return jsonify({"message": f"User '{email}' updated successfully"}), 200

@app.route("/api/users/<string:email>", methods=["DELETE"])
def delete_user(email):
    success = User.delete_user(email)
    if not success:
        return jsonify({"error": "User not found"}), 404
    save_users()
    if email in shopping_carts:
        del shopping_carts[email]
    return jsonify({"message": f"User '{email}' deleted"}), 200

# ---------------------------
# CART ENDPOINTS
# ---------------------------
@app.route("/api/cart/<string:user_email>", methods=["GET"])
def get_cart(user_email):
    cart = shopping_carts.get(user_email)
    if not cart:
        return jsonify({"error": "Cart not found"}), 404
    items = []
    # Assumes cart.root._children holds the cart items
    for item in cart.root._children:
        items.append({
            "name": item.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
        })
    return jsonify(items), 200

@app.route("/api/cart/<string:user_email>", methods=["PUT"])
def update_cart(user_email):
    data = request.get_json()
    item_name = data.get("name")
    new_quantity = data.get("quantity")
    cart = shopping_carts.get(user_email)
    if not cart:
        return jsonify({"error": "Cart not found"}), 404
    updated = False
    for item in cart.root._children:
        if item.name == item_name:
            item.quantity = new_quantity
            updated = True
            break
    if not updated:
        return jsonify({"error": "Item not found in cart"}), 404
    return jsonify({"message": "Cart updated"}), 200

@app.route("/api/cart/<string:user_email>", methods=["DELETE"])
def delete_cart_item(user_email):
    data = request.get_json()
    item_name = data.get("name")
    cart = shopping_carts.get(user_email)
    if not cart:
        return jsonify({"error": "Cart not found"}), 404
    initial_count = len(cart.root._children)
    cart.root._children = [item for item in cart.root._children if item.name != item_name]
    if len(cart.root._children) == initial_count:
        return jsonify({"error": "Item not found in cart"}), 404
    return jsonify({"message": "Item deleted from cart"}), 200

# ---------------------------
# ORDER ENDPOINTS
# ---------------------------
@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    user_email = data.get("user_email")
    item_list = data.get("items", [])
    payment_method = data.get("payment_method", "Credit Card")
    user = User.get_user(user_email)
    if not user:
        return jsonify({"error": "User does not exist"}), 404

    # Use the user's shopping cart if it exists; otherwise create one
    if user_email in shopping_carts:
        cart = shopping_carts[user_email]
    else:
        cart = ShoppingCart()
        shopping_carts[user_email] = cart

    inv = Inventory.get_instance()

    # For each item in the order request, add it to the cart.
    for item_info in item_list:
        fname = item_info.get("name")
        qty = int(item_info.get("quantity", 1))
        furniture_obj = None
        for fobj in inv.items:
            if fobj.name == fname:
                furniture_obj = fobj
                break
        if not furniture_obj:
            return jsonify({"error": f"No furniture found with name '{fname}'"}), 400
        leaf = LeafItem(fname, furniture_obj.price, qty)
        cart.add_item(leaf)

    checkout = Checkout(user, cart, inv)
    checkout.set_payment_method(payment_method)
    checkout.set_address(user.address)
    if not checkout.validate_cart():
        return jsonify({"error": "Not enough stock or invalid items"}), 400
    if not checkout.process_payment():
        return jsonify({"error": "Payment failed"}), 400
    if not checkout.finalize_order():
        return jsonify({"error": "Could not finalize order"}), 400

    # Gather leaf items from the cart for the order record.
    leaf_items = []
    for component in cart.root._children:
        if isinstance(component, LeafItem):
            leaf_items.append(component)
    new_order = Order(
        user=user,
        items=leaf_items,
        total_price=cart.get_total_price(),
        status=OrderStatus.PENDING
    )
    orders.append(new_order)
    # Update the user's order history (ensure it's iterable)
    if user.order_history is None:
        user.order_history = []
    user.order_history.append(new_order)
    save_inventory()
    return jsonify({
        "message": f"Order created successfully for {user.email}",
        "order_status": new_order.status.value,
        "total_price": new_order.total_price,
    }), 201

@app.route("/api/orders", methods=["GET"])
def get_orders():
    output = []
    for o in orders:
        output.append({
            "user_email": o.user.email,
            "status": o.status.value,
            "total_price": o.total_price,
            "items": [
                {"name": i.name, "quantity": i.quantity, "price_each": i.unit_price}
                for i in o.items
            ],
            "created_at": o.created_at.isoformat() if hasattr(o, 'created_at') else ""
        })
    return jsonify(output), 200

# ---------------------------
# RUN THE APP
# ---------------------------
if __name__ == "__main__":
    print("Starting the Flask app with Catalog-based data model...")
    app.run(debug=True)
