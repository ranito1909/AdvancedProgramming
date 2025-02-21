from flask import Flask, request, jsonify
import os
import pickle

# Import everything you need from Catalog.py
# (Adjust the import statement according to your actual module/file name)
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
    Checkout,
)

app = Flask(__name__)

# --------------------------------------------------------------------
# Optional: paths for persisting the Inventory and Users
# --------------------------------------------------------------------
INVENTORY_PICKLE = "inventory.pkl"
USERS_PICKLE = "users.pkl"

# --------------------------------------------------------------------
# Helper methods to load/save the Inventory singleton and User data
# --------------------------------------------------------------------
def load_inventory():
    """
    Loads the entire Inventory singleton from a pickle file, if it exists.
    Otherwise, just returns the singleton with an empty items dict.
    """
    if os.path.exists(INVENTORY_PICKLE):
        with open(INVENTORY_PICKLE, "rb") as f:
            loaded_items = pickle.load(f)  # This should be a dict of Furniture->int
        # Inventory is a singleton; get the instance, then set its items
        inv = Inventory.get_instance()
        inv.items = loaded_items
    else:
        Inventory.get_instance()  # ensure it's created

def save_inventory():
    """
    Saves the singleton Inventory's items dictionary to a pickle file.
    """
    inv = Inventory.get_instance()
    with open(INVENTORY_PICKLE, "wb") as f:
        pickle.dump(inv.items, f)

def load_users():
    """
    Loads the dictionary of users (User._users) from a pickle file, if it exists.
    """
    if os.path.exists(USERS_PICKLE):
        with open(USERS_PICKLE, "rb") as f:
            user_dict = pickle.load(f)
        # user_dict is expected to be {email: User object, ...}
        User._users = user_dict
    else:
        User._users = {}

def save_users():
    """
    Saves the dictionary of users (User._users) to a pickle file.
    """
    with open(USERS_PICKLE, "wb") as f:
        pickle.dump(User._users, f)


# --------------------------------------------------------------------
# Before the first request, we load data into memory from pickle files
# --------------------------------------------------------------------
@app.before_request
def initialize_data():
     if not hasattr(app, 'initialized'):
        load_inventory()
        load_users()
        app.initialized = True


# --------------------------------------------------------------------
# FURNITURE / INVENTORY ROUTES
# --------------------------------------------------------------------
@app.route("/api/furniture", methods=["GET"])
def get_furniture():
    """
    Return a list of all furniture in our Inventory, along with its quantity.
    """
    inv = Inventory.get_instance()
    response = []
    for furniture_obj, qty in inv.items.items():
        response.append({
            "name": furniture_obj.name,
            "type": type(furniture_obj)._name_,
            "description": furniture_obj.description,
            "price": furniture_obj.price,
            "dimensions": furniture_obj.dimensions,
            "quantity": qty,
        })
    return jsonify(response), 200


@app.route("/api/furniture", methods=["POST"])
def add_furniture():
    """
    Create a new piece of furniture and add it to the Inventory.
    The JSON body should specify 'type' (Chair, Table, Sofa, Lamp, Shelf), etc.
    Example body:
      {
        "type": "Chair",
        "name": "Office Chair",
        "description": "Ergonomic rolling chair",
        "price": 300,
        "dimensions": [20, 20, 40],
        "extra_attr": "Leather",  # e.g. cushion_material for Chair
        "quantity": 5
      }
    """
    data = request.get_json()

    ftype = data.get("type")
    name = data.get("name")
    desc = data.get("description", "")
    price = float(data.get("price", 0))
    dims = tuple(data.get("dimensions", []))
    qty = int(data.get("quantity", 1))

    # 'extra_attr' might represent cushion material, frame material, etc., 
    # depending on the furniture type.
    extra = data.get("extra_attr", "")

    # Create the appropriate furniture object
    if ftype == "Chair":
        furniture_obj = Chair(name, desc, price, dims, cushion_material=extra)
    elif ftype == "Table":
        furniture_obj = Table(name, desc, price, dims, frame_material=extra)
    elif ftype == "Sofa":
        capacity = int(extra) if extra else 3  # or parse differently
        furniture_obj = Sofa(name, desc, price, dims, capacity)
    elif ftype == "Lamp":
        furniture_obj = Lamp(name, desc, price, dims, light_source=extra)
    elif ftype == "Shelf":
        wall_mounted = bool(extra.lower() == "true")  # or parse differently
        furniture_obj = Shelf(name, desc, price, dims, wall_mounted)
    else:
        return jsonify({"error": "Unsupported furniture type"}), 400

    # Add to inventory
    inv = Inventory.get_instance()
    inv.add_item(furniture_obj, quantity=qty)
    save_inventory()  # persist the change

    return jsonify({"message": f"{ftype} '{name}' added with quantity {qty}"}), 201


@app.route("/api/furniture/<string:name>", methods=["PUT"])
def update_furniture(name):
    """
    Update an existing furniture's price, description, or quantity by name.
    Example body:
      {
        "price": 450,
        "description": "Updated description",
        "quantity": 10
      }
    """
    data = request.get_json()

    inv = Inventory.get_instance()

    # Find the matching Furniture object by name
    furniture_obj = None
    for fobj in inv.items.keys():
        if fobj.name == name:
            furniture_obj = fobj
            break

    if not furniture_obj:
        return jsonify({"error": "Furniture not found"}), 404

    # Update fields
    new_price = data.get("price")
    new_desc = data.get("description")
    new_qty = data.get("quantity")

    if new_price is not None:
        furniture_obj.price = float(new_price)

    if new_desc is not None:
        furniture_obj.description = new_desc

    if new_qty is not None:
        # Update quantity in inventory
        success = inv.update_quantity(furniture_obj, int(new_qty))
        if not success:
            return jsonify({"error": "Failed to update quantity"}), 400

    save_inventory()
    return jsonify({"message": f"Furniture '{name}' updated successfully"}), 200


@app.route("/api/furniture/<string:name>", methods=["DELETE"])
def delete_furniture(name):
    """
    Remove an existing furniture item entirely from the inventory by name.
    """
    inv = Inventory.get_instance()
    furniture_obj = None

    for fobj in list(inv.items.keys()):
        if fobj.name == name:
            furniture_obj = fobj
            break

    if not furniture_obj:
        return jsonify({"error": "Furniture not found"}), 404

    # Remove it from inventory completely
    inv.remove_item(furniture_obj, quantity=inv.items[furniture_obj])
    save_inventory()
    return jsonify({"message": f"Furniture '{name}' removed from inventory"}), 200


# --------------------------------------------------------------------
# USER ROUTES
# --------------------------------------------------------------------
@app.route("/api/users", methods=["GET"])
def get_users():
    """
    Return a list of all users (their basic info).
    """
    all_users = []
    for user in User._users.values():
        all_users.append({
            "email": user.email,
            "name": user.name,
            "address": user.address,
            "order_history": user.order_history,
        })
    return jsonify(all_users), 200


@app.route("/api/users", methods=["POST"])
def register_user():
    """
    Create a new user in the system. 
    Example body:
      {
         "name": "Alice",
         "email": "alice@example.com",
         "password": "secret123",
         "address": "Some address"
      }
    """
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    address = data.get("address", "")

    if not (name and email and password):
        return jsonify({"error": "Missing required fields"}), 400

    # Attempt to register via the Catalog User class
    try:
        user = User.register_user(name, email, password, address=address)
        save_users()  # persist the user dictionary
        return jsonify({"message": f"User '{email}' registered successfully"}), 201
    except ValueError as e:
        # This is raised if user with the same email already exists
        return jsonify({"error": str(e)}), 400


@app.route("/api/login", methods=["POST"])
def login_user():
    """
    Basic login. 
    Example body:
      {
        "email": "alice@example.com",
        "password": "secret123"
      }
    """
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
    """
    Update an existing user's name or address.
    Example body:
      {
        "name": "New Name",
        "address": "New Address"
      }
    """
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
    """
    Delete a user from the system entirely.
    """
    success = User.delete_user(email)
    if not success:
        return jsonify({"error": "User not found"}), 404
    save_users()
    return jsonify({"message": f"User '{email}' deleted"}), 200


# --------------------------------------------------------------------
# A SIMPLE EXAMPLE: CREATE AN ORDER (DEMO)
# --------------------------------------------------------------------
# In a real system, you might want a separate class for Order management,
# plus a route to handle shipping, statuses, etc. This is just a sample.
orders = []  # store Order objects in memory for demonstration


@app.route("/api/orders", methods=["POST"])
def create_order():
    """
    Creates an order for a given user, with a list of items.
    Example body:
      {
        "user_email": "alice@example.com",
        "items": [
          {"name": "Office Chair", "quantity": 2},
          {"name": "Coffee Table", "quantity": 1}
        ],
        "payment_method": "Credit Card"
      }
    This endpoint demonstrates how to tie it all together using the classes from Catalog.
    """
    data = request.get_json()
    user_email = data.get("user_email")
    item_list = data.get("items", [])
    payment_method = data.get("payment_method", "Credit Card")

    user = User.get_user(user_email)
    if not user:
        return jsonify({"error": "User does not exist"}), 404

    # Build a ShoppingCart
    cart = ShoppingCart()
    inv = Inventory.get_instance()

    # For each requested item, find matching Furniture in the inventory
    for item_info in item_list:
        fname = item_info.get("name")
        qty = int(item_info.get("quantity", 1))

        # Look up the furniture object by name
        furniture_obj = None
        for fobj in inv.items:
            if fobj.name == fname:
                furniture_obj = fobj
                break
        if not furniture_obj:
            return jsonify({"error": f"No furniture found with name '{fname}'"}), 400

        # Create a LeafItem representing the purchase of that furniture
        leaf = LeafItem(fname, furniture_obj.price, qty)
        cart.add_item(leaf)

    # Now let's do the checkout
    checkout = Checkout(user, cart, inv)
    checkout.set_payment_method(payment_method)
    checkout.set_address(user.address)  # or some shipping address from data

    # Validate inventory (make sure everything is in stock)
    if not checkout.validate_cart():
        return jsonify({"error": "Not enough stock or invalid items"}), 400

    # Process payment (mock)
    paid = checkout.process_payment()
    if not paid:
        return jsonify({"error": "Payment failed"}), 400

    # Finalize order -> updates inventory, adds to user history, etc.
    success = checkout.finalize_order()
    if not success:
        return jsonify({"error": "Could not finalize order"}), 400

    # If we got here, the order is complete
    # Create an Order object for demonstration
    # (You can store it however you like—DB, list in memory, etc.)
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

    # Persist the updated inventory
    save_inventory()

    return jsonify({
        "message": f"Order created successfully for {user.email}",
        "order_status": new_order.status.value,
        "total_price": new_order.total_price,
    }), 201


@app.route("/api/orders", methods=["GET"])
def get_orders():
    """
    Return a basic list of all in-memory orders for demonstration.
    In a real app, you'd likely store these in a DB or in the user's own order history.
    """
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
            "created_at": o.created_at.isoformat()
        })
    return jsonify(output), 200


# --------------------------------------------------------------------
# RUN
# --------------------------------------------------------------------
if __name__ == "_main_":
    print("Starting the Flask app with Catalog-based data model...")
    app.run(debug=True)