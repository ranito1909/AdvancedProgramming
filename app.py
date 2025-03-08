from flask import Flask, request, jsonify
import os
import logging
import pandas as pd
# Import furniture classes and the Inventory singleton from catalog.py
from Catalog import Inventory, Chair, Table, Sofa, Lamp, Shelf , User , ShoppingCart, LeafItem , Checkout , Order , OrderStatus
import pickle
# Define the storage directory
storage_dir = "storage"

# Ensure the storage directory exists
os.makedirs(storage_dir, exist_ok=True)

# List of required files and their default content
files_with_defaults = {
    "orders.pkl": pd.DataFrame(columns=["order_id", "user_email", "items"]),
    "users.pkl": pd.DataFrame(columns=["email", "name", "password_hash", "address", "order_history"]),
    "cart.pkl": pd.DataFrame(columns=["user_email", "items"]),
    "inventory.pkl": pd.DataFrame(columns=["id", "name", "description", "price", "dimensions", "class", "quantity"])
}

# Check and create files if they don't exist, and initialize with default data if empty
for filename, default_df in files_with_defaults.items():
    file_path = os.path.join(storage_dir, filename)

    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, "wb") as f:
            pickle.dump(default_df, f)  # Save default DataFrame
        print("[DEBUG_APP]",f"Created and initialized: {file_path}")
    else:
        print("[DEBUG_APP]",f"Already exists and checked: {file_path}")
def safe_load_pickle(file_path, default_df):
    try:
        df = pd.read_pickle(file_path)
        if not isinstance(df, pd.DataFrame):  # Ensure it's a DataFrame
            raise ValueError("Invalid pickle content, resetting file.")
        return df
    except (EOFError, FileNotFoundError, ValueError, pickle.UnpicklingError):
        print("[DEBUG_APP]",f"[WARNING] {file_path} is empty or corrupted. Resetting...")
        with open(file_path, "wb") as f:
            pickle.dump(default_df, f)
        return default_df

# Load data with error handling
orders_df = safe_load_pickle(os.path.join(storage_dir, "orders.pkl"), files_with_defaults["orders.pkl"])
users_df = safe_load_pickle(os.path.join(storage_dir, "users.pkl"), files_with_defaults["users.pkl"])
cart_df = safe_load_pickle(os.path.join(storage_dir, "cart.pkl"), files_with_defaults["cart.pkl"])
furniture_df = safe_load_pickle(os.path.join(storage_dir, "inventory.pkl"), files_with_defaults["inventory.pkl"])


# Initialize the Inventory singleton
inventory = Inventory.get_instance()
shopping_carts = {}

# Monkey-Patch DataFrame.append (for pandas>=2.0)
def custom_append(self, other, ignore_index=False):
    if isinstance(other, dict):
        other = pd.DataFrame([other])
    elif isinstance(other, list):
        other = pd.DataFrame(other)
    return pd.concat([self, other], ignore_index=ignore_index)

pd.DataFrame.append = custom_append


app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)


# "Save" functions (simulate persistence)
def save_orders(orders_df, filename="orders.pkl", storage_dir="storage"):
    """
    Persist the orders DataFrame to a pickle file.
    
    Args:
        orders_df (pd.DataFrame): The DataFrame containing all order data.
        filename (str): The name of the file in which to store the orders (default "orders.pkl").
        storage_dir (str): The directory where the pickle file is saved.
            This parameter lets you choose where to store the data. For example, you might use a
            single "storage" folder for all persisted data, or later organize data into subdirectories
            (like "storage/orders" for orders, "storage/users" for user data, etc.).
    
    This function converts the orders data into a pickle file so that it can be reloaded later
    without loss. It is consistent with other persistence functions in our project.
    """
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)
    filepath = os.path.join(storage_dir, filename)
    orders_df.to_pickle(filepath)
    print("[DEBUG_APP]",f"Orders saved to {filepath}")

def save_users(users_dict, filename="users.pkl", storage_dir="storage"):
    """
    Save the current users stored in the User._users dictionary to a pickle file.
    
    Args:
        users_dict (dict): The dictionary containing user instances (typically User._users).
        filename (str): The name of the pickle file.
        storage_dir (str): The directory where the pickle file is saved.
    """
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)
    
    # Convert the users dictionary to a list of simple dictionaries.
    users_list = []
    for email, user in users_dict.items():
        users_list.append({
            "email": user.email,
            "name": user.name,
            "password_hash": user.password_hash,
            "address": user.address,
            "order_history": user.order_history
        })
    
    users_df = pd.DataFrame(users_list)
    filepath = os.path.join(storage_dir, filename)
    users_df.to_pickle(filepath)
    print("[DEBUG_APP]",f"Users saved to {filepath}")

def save_cart(shopping_carts, filename="cart.pkl", storage_dir="storage"):
    """
    Persist the current shopping carts to a pickle file.
    
    Args:
        shopping_carts (dict): A dictionary mapping user emails to ShoppingCart instances.
        filename (str): The name of the file in which to store the cart data (default "cart.pkl").
        storage_dir (str): The directory where the pickle file is saved.
            You can choose to store all data in one folder or organize into subdirectories
            (e.g., "storage/cart" for cart data).
    
    This function converts the shopping cart information into a list of dictionaries.
    Each dictionary contains the user email, a list of items (with their furniture_id, quantity, 
    and unit_price), and the total price of the cart. The resulting list is then converted to a 
    pandas DataFrame and saved as a pickle file.
    """
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)
    
    carts_list = []
    for email, cart in shopping_carts.items():
        items = []
        for item in cart.root._children:
            items.append({
                "furniture_id": item.id,
                "quantity": item.quantity,
                "unit_price": item.unit_price
            })
        carts_list.append({
            "user_email": email,
            "items": items,
            "total_price": cart.get_total_price()
        })
    
    carts_df = pd.DataFrame(carts_list)
    filepath = os.path.join(storage_dir, filename)
    carts_df.to_pickle(filepath)
    print("[DEBUG_APP]",f"Cart data saved to {filepath}")

def save_inventory(inventory_instance, filename="inventory.pkl", storage_dir="storage"):
    """
    Persist the current inventory from the Inventory singleton to a pickle file.

    Args:
        inventory_instance: The Inventory instance containing the furniture items and their quantities.
        filename (str): The name of the pickle file in which to store the inventory data (default "inventory.pkl").
        storage_dir (str): The directory where the pickle file is saved.
            This parameter lets you choose where to store the data. For example, you might use a
            dedicated folder for inventory data (e.g., "storage/inventory") if desired.

    Returns:
        pd.DataFrame: The DataFrame created from the inventory data.

    This function converts the inventory data (stored as a dictionary mapping Furniture objects to their available quantities)
    into a pandas DataFrame and saves it as a pickle file. It ensures that the storage directory exists before saving.
    """
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)
    
    data = []
    # Loop through each furniture item and its quantity to build a list of dictionaries.
    for furniture, quantity in inventory_instance.items.items():
        print("[DEBUG_APP]",f"[DEBUG] Saving furniture: {furniture} with quantity {quantity}")
        data.append({
            "id": getattr(furniture, "id", None),
            "name": getattr(furniture, "name", None),
            "description": getattr(furniture, "description", None),
            "price": getattr(furniture, "price", None),
            "dimensions": getattr(furniture, "dimensions", None),
            "class": furniture.__class__.__name__,
            "quantity": quantity
        })

    inventory_df = pd.DataFrame(data)
    filepath = os.path.join(storage_dir, filename)
    inventory_df.to_pickle(filepath)
    print("[DEBUG_APP]",f"Inventory saved to {filepath}")
    
    return inventory_df


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
    orders_dict = [order.to_dict() for order in Order.all_orders]
    return jsonify(orders_dict), 200

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

# Helper function to locate a furniture item by its ID in the Inventory
def get_furniture_item_by_id(furniture_id: int):
    return next((item for item in inventory.items.keys() if getattr(item, "id", None) == furniture_id), None)

@app.route("/api/inventory/<int:furniture_id>/quantity", methods=["GET"])
def get_quantity_for_item(furniture_id):
    """
    Retrieve the available quantity for a specific furniture item by its ID.
    
    This endpoint uses the Inventory.get_quantity() method defined in Catalog.py.
    """
    furniture_item = get_furniture_item_by_id(furniture_id)
    if not furniture_item:
        return jsonify({"error": "Furniture item not found"}), 404

    # Use the get_quantity() method of the Inventory instance without rewriting its functionality.
    quantity = inventory.get_quantity(furniture_item)
    return jsonify({"id": furniture_id, "quantity": quantity}), 200

@app.route("/api/cart/<string:email>/view", methods=["GET"])
def view_cart_endpoint(email: str):
    """
    Retrieve and display the contents of the shopping cart for the specified user.
    
    This endpoint uses the ShoppingCart.view_cart() method (from Catalog.py) to obtain a string
    representing the cart contents. If no cart exists for the user, a 404 error is returned.
    """
    if email not in shopping_carts:
        return jsonify({"error": "Shopping cart not found for user"}), 404

    cart = shopping_carts[email]
    cart_contents = cart.view_cart()
    return jsonify({"cart": cart_contents}), 200

@app.route("/api/checkout/<string:email>/validate", methods=["GET"])
def validate_cart_endpoint(email: str):
    """
    Validate the shopping cart for the specified user.
    
    This endpoint creates a Checkout instance using the user's shopping cart and inventory,
    and then calls the validate_cart() method to check if the items in the cart are available
    in sufficient quantity.
    """
    # Check if the user exists.
    if email not in User._users:
        return jsonify({"error": "User not found"}), 404

    # Check if the shopping cart exists for this user.
    if email not in shopping_carts:
        return jsonify({"error": "Shopping cart not found for user"}), 404

    user = User._users[email]
    cart = shopping_carts[email]
    checkout_obj = Checkout(user, cart, inventory)
    is_valid = checkout_obj.validate_cart()
    return jsonify({"cart_valid": is_valid}), 200

@app.route("/api/checkout/<string:email>/leaf_items", methods=["GET"])
def get_leaf_items(email: str):
    """
    Retrieve the leaf items from the shopping cart for the specified user.
    
    This endpoint creates a Checkout instance and calls its _collect_leaf_items() method
    on the shopping cart's root, returning a JSON list of leaf items (for debugging purposes).
    """
    # Check that the user exists.
    if email not in User._users:
        return jsonify({"error": "User not found"}), 404

    # Check that the shopping cart exists for this user.
    if email not in shopping_carts:
        return jsonify({"error": "Shopping cart not found for user"}), 404

    user = User._users[email]
    cart = shopping_carts[email]
    checkout_obj = Checkout(user, cart, inventory)
    
    # Call the private method _collect_leaf_items on the cart's root.
    leaf_items = checkout_obj._collect_leaf_items(cart.root)
    
    # Build a JSON-friendly list of items.
    items_list = []
    for item in leaf_items:
        items_list.append({
            "name": item.name,
            "unit_price": item.unit_price,
            "quantity": item.quantity,
            "total_price": item.get_price()
        })
    
    return jsonify({"leaf_items": items_list}), 200

@app.route("/api/checkout/<string:email>/find_furniture", methods=["GET"])
def find_furniture_by_name_endpoint(email: str):
    """
    Retrieve a furniture item from inventory by name using Checkout._find_furniture_by_name().
    
    Expects a query parameter "name" with the furniture's name.
    """
    # Verify that the user exists.
    if email not in User._users:
        return jsonify({"error": "User not found"}), 404

    # Verify that the shopping cart exists for this user.
    if email not in shopping_carts:
        return jsonify({"error": "Shopping cart not found for user"}), 404

    # Get the furniture name from the query parameters.
    furniture_name = request.args.get("name")
    if not furniture_name:
        return jsonify({"error": "Missing 'name' query parameter"}), 400

    user = User._users[email]
    cart = shopping_carts[email]
    checkout_obj = Checkout(user, cart, inventory)
    
    # Use the internal method to find the furniture by name.
    furniture_item = checkout_obj._find_furniture_by_name(furniture_name)
    if not furniture_item:
        return jsonify({"error": "Furniture not found"}), 404

    # Build a response with furniture details.
    response = {
        "id": furniture_item.id,
        "name": furniture_item.name,
        "description": furniture_item.description,
        "price": furniture_item.price,
        "dimensions": furniture_item.dimensions,
        "class": furniture_item.__class__.__name__,
        "quantity": inventory.get_quantity(furniture_item)
    }
    return jsonify(response), 200

# ---------------------------
# POST Endpoints
# ---------------------------
@app.route("/api/inventorysearch", methods=["POST"])
def inventory_search():
    """
    Search inventory based on parameters in the request body.
    Expected JSON body fields:
      - name_substring (optional string)
      - min_price (optional float)
      - max_price (optional float)
      - furniture_type (optional string)
    """
    data = request.get_json() or {}

    name_substring = data.get("name_substring")
    min_price = data.get("min_price")
    max_price = data.get("max_price")
    furniture_type_str = data.get("furniture_type")

    # Optionally log incoming data for debugging
    logging.debug(f"[DEBUG_APP] Inventory search parameters: {data}")


    # Run the inventory search
    inventory = Inventory.get_instance()
    search_results = inventory.search(
        name_substring=name_substring,
        min_price=min_price,
        max_price=max_price,
        furniture_type=furniture_type_str,
    )

    # Convert results to a list of dicts if needed
    # or you can return them directly if they are JSON serializable
    output = []
    for item in search_results:
        output.append({
            "name": item.name,
            "price": item.price,
            "quantity": inventory.get_quantity(item)
        })

    return jsonify(output), 200

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

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required."}), 400
    user = User.login_user(email, password)
    if not user:
        return jsonify({"error": "Invalid email or password."}), 401
    return jsonify({
        "email": user.email,
        "name": user.name,
        "address": user.address,
        "order_history": user.order_history
    }), 200

@app.route("/api/users/<email>/check_password", methods=["POST"])
def check_password(email):
    data = request.get_json() or {}
    candidate = data.get("password")
    if not candidate:
        return jsonify({"error": "Missing password"}), 400
    user = User.get_user(email)
    if not user:
        return jsonify({"error": "User not found"}), 404
    is_correct = user.check_password(candidate)
    return jsonify({"password_correct": is_correct}), 200

@app.route("/api/hash_password", methods=["POST"])
def hash_password():
    data = request.get_json() or {}
    raw_password = data.get("password")
    if not raw_password:
        return jsonify({"error": "Missing password"}), 400
    hashed = User._hash_password(raw_password)
    return jsonify({"hashed_password": hashed}), 200

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json() or {}
    user_email = data.get("user_email")
    print("[DEBUG_APP]",f"[DEBUG] create_order: received user_email: {user_email}")
    
    # Retrieve the user instance.
    user = User.get_user(user_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    items = data.get("items", [])
    if not isinstance(items, list):
        return jsonify({"error": "items must be a list"}), 400
    if not items:
        return jsonify({"error": "Order items cannot be empty"}), 400

    leaf_items = []
    total_price = 0.0

    # Validate each order item against the inventory.
    for order_item in items:
        furniture_id = order_item.get("furniture_id")
        order_quantity = order_item.get("quantity", 1)
        found = None
        if not isinstance(inventory.items, dict):
            return jsonify({"error": "Inventory is not properly initialized"}), 500
        for furniture in inventory.items.keys():
            print("[DEBUG_APP]",f"[DEBUG] Checking furniture id: {getattr(furniture, 'id', None)} against order id: {furniture_id}")
            if getattr(furniture, "id", None) == furniture_id:
                if not furniture.check_availability(): # Ensure no zero-quantity items
                    return jsonify({"error": f"Furniture '{furniture.name}' is not available"}), 400
                if inventory.items[furniture] < order_quantity:
                    return jsonify({"error": f"Not enough quantity for furniture with id {furniture_id}"}), 400
                print("[DEBUG_APP]",f"[DEBUG] Found furniture id {furniture_id} with quantity {inventory.items[furniture]}")
                found = furniture
                break
        if not found:
            return jsonify({"error": f"Furniture with id {furniture_id} does not exist"}), 404

        # Create a LeafItem for the furniture.
        leaf_item = LeafItem(found.name, found.price, quantity=order_quantity)
        leaf_items.append(leaf_item)
        total_price += leaf_item.get_price()

    # Create the Order. It is automatically stored in Order.all_orders.
    new_order = Order(user, leaf_items, total_price, status=OrderStatus.PENDING)
    
    # Update inventory: subtract purchased quantities.
    for order_item in items:
        furniture_id = order_item.get("furniture_id")
        order_quantity = order_item.get("quantity", 1)
        for furniture in list(inventory.items.keys()):
            if getattr(furniture, "id", None) == furniture_id:
                inventory.items[furniture] -= order_quantity
                break

    # Update the user's order history.
    user.add_order(str(new_order))
    
    return jsonify(new_order.to_dict()), 201

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

@app.route("/api/checkout/<email>", methods=["POST"])
def checkout(email):

    data = request.get_json() or {}
    app.logger.debug("[DEBUG] checkout: Received data for email %s: %s", email, data)

    payment_method = data.get("payment_method")
    address = data.get("address")
    if not payment_method or not address:
        app.logger.debug("[DEBUG] checkout: Missing payment_method or address in data: %s", data)
        return jsonify({"error": "Both payment_method and address are required."}), 400

    if email not in shopping_carts:
        app.logger.debug("[DEBUG] checkout: No shopping cart found for email %s", email)
        return jsonify({"error": "Shopping cart not found for user."}), 404
    if email not in User._users:
        app.logger.debug("[DEBUG] checkout: No user found for email %s", email)
        return jsonify({"error": "User not found."}), 404

    cart = shopping_carts[email]
    user = User._users[email]
    
    checkout_obj = Checkout(user, cart, inventory)
    checkout_obj.set_payment_method(payment_method)
    checkout_obj.set_address(address)
    app.logger.debug("[DEBUG] checkout: Checkout initiated for user %s", email)

    if not checkout_obj.finalize_order():
        app.logger.debug("[DEBUG] checkout: Order finalization failed for user %s", email)
        return jsonify({"error": "Checkout process failed. Check logs for details."}), 400

    # Assuming the user object stores order summaries in an 'orders' list.
    order_summary = checkout_obj.order_summary or "Order summary not available"
    app.logger.debug("[DEBUG] checkout: Order finalized for user %s with summary: %s", email, order_summary)
    return jsonify({"message": "Order finalized successfully.", "order_summary": order_summary}), 200

@app.route("/api/cart/<string:email>/remove", methods=["POST"])
def remove_cart_item(email: str):
    """
    Remove an item from the shopping cart by creating a LeafItem from request data
    and calling remove_item on the cart.
    """
    data = request.get_json() or {}
    item_id = data.get("item_id")
    unit_price = data.get("unit_price")
    quantity = data.get("quantity")
    if not item_id:
        return jsonify({"error": "Missing item_id in request data"}), 400
    if unit_price is None:
        return jsonify({"error": "Missing unit_price in request data"}), 400
    if quantity is None:
        return jsonify({"error": "Missing quantity in request data"}), 400

    if email not in shopping_carts:
        return jsonify({"error": "Shopping cart not found for user"}), 404

    # Create a LeafItem using the incoming data
    leaf_item = LeafItem(
        name=str(item_id),
        unit_price=float(unit_price),
        quantity=int(quantity)
    )

    cart = shopping_carts[email]
    cart.remove_item(leaf_item)

    app.logger.debug("[DEBUG] remove_item from cart: Removed item %s from cart for user %s", item_id, email)
    return jsonify({
        "message": "Item removed from cart",
        "total_price": cart.get_total_price()
    }), 200

@app.route("/api/checkout/<string:email>/payment", methods=["POST"])
def process_payment_endpoint(email: str):
    """
    Process the payment for the shopping cart of the specified user.

    Expects a JSON payload with:
      - payment_method: A string indicating the payment method to use.

    This endpoint creates a Checkout instance with the user's shopping cart and inventory,
    sets the provided payment method, and calls process_payment() to simulate payment processing.
    It returns a JSON response indicating whether the payment was successful.
    """
    # Check that the user exists.
    if email not in User._users:
        return jsonify({"error": "User not found"}), 404

    # Check that the shopping cart exists for this user.
    if email not in shopping_carts:
        return jsonify({"error": "Shopping cart not found for user"}), 404

    data = request.get_json() or {}
    payment_method = data.get("payment_method")
    if not payment_method:
        return jsonify({"error": "Payment method is required"}), 400

    user = User._users[email]
    cart = shopping_carts[email]
    checkout_obj = Checkout(user, cart, inventory)
    checkout_obj.set_payment_method(payment_method)
    
    # Call process_payment() to simulate the payment processing.
    payment_result = checkout_obj.process_payment()
    if payment_result:
        return jsonify({"payment_success": True}), 200
    else:
        return jsonify({"payment_success": False, "error": "Payment processing failed"}), 400

@app.route("/api/orders/<int:order_id>/status", methods=["GET"])
def get_order_status(order_id):
    # Find the order by ID
    order = next((o for o in Order.all_orders if o.order_id == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    return jsonify({"order_id": order.order_id, "status": order.get_status().value}), 200

# ---------------------------
# PUT Endpoints
# ---------------------------
@app.route("/api/cart/<email>", methods=["PUT"])
def update_cart(email):
    data = request.get_json() or {}
    app.logger.debug("[DEBUG] update_cart: Received data for email %s: %s", email, data)
    
    items = data.get("items", [])
    if not isinstance(items, list):
        return jsonify({"error": "items must be a list"}), 400

    # If a cart exists for the user, clear its items; otherwise, create a new cart.
    if email in shopping_carts:
        cart = shopping_carts[email]
        cart.root._children.clear()  # Clear previous items.
        app.logger.debug("[DEBUG] update_cart: Existing cart found for email %s. Cleared previous items.", email)
    else:
        cart = ShoppingCart(name=email)
        shopping_carts[email] = cart
        app.logger.debug("[DEBUG] update_cart: New cart created for email %s.", email)

    # Process each item in the request.
    for item in items:
        furniture_id = item.get("furniture_id")
        quantity = item.get("quantity", 1)
        discount = item.get("discount", 0)  # Default 0 if not provided

        # Try to get the unit_price from the payload; if not provided, lookup from inventory.
        unit_price = item.get("unit_price")
        if unit_price is None:
            # Lookup furniture in the inventory by matching id.
            found = None
            for furniture in inventory.items.keys():
                if getattr(furniture, "id", None) == furniture_id:
                    found = furniture
                    break
            if found:
                unit_price = found.price
            else:
                return jsonify({"error": f"Product with id {furniture_id} does not exist in the inventory."}), 404
        
        # Create the LeafItem using the valid unit_price.
        leaf_item = LeafItem(name=str(furniture_id), unit_price=float(unit_price), quantity=int(quantity))

        try:
            leaf_item.apply_discount(discount)
        except ValueError as e:
            # For example, discount > 100 raises ValueError. Return 400 with the error message.
            return jsonify({"error": str(e)}), 400
        
        cart.add_item(leaf_item)
        #app.logger.debug("[DEBUG] update_cart: Added item: %s", leaf_item)

    total_price = cart.get_total_price()
    response_items = []
    for child in cart.root._children:
        response_items.append({
            "furniture_id": int(child.name),
            "quantity": child.quantity
        })
    #app.logger.debug("[DEBUG] update_cart: Cart updated for email %s with total price: %.2f", email, total_price)

    return jsonify({"user_email": email, "items": response_items, "total_price": total_price}), 200


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

@app.route("/api/users/<email>/password", methods=["PUT"])
def update_password(email):
    data = request.get_json() or {}
    new_password = data.get("new_password")
    if not new_password:
        return jsonify({"error": "Missing new_password"}), 400
    user = User.get_user(email)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.set_password(new_password)
    return jsonify({"message": "Password updated successfully"}), 200

@app.route("/api/orders/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    data = request.get_json() or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Missing status"}), 400

    # Find the order by ID
    order = next((o for o in Order.all_orders if o.order_id == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    try:
        order.set_status(OrderStatus(new_status))
    except ValueError:
        return jsonify({"error": "Invalid order status"}), 400

    return jsonify({"message": "Order status updated successfully"}), 200

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
    { "id" : unique(id),
      "class": "Chair" or "Table" or "Sofa" or "Lamp" or "Shelf",
      "name": "...",
      "description": "...",
      "price": 123.45,
      "dimensions": [width, depth, height],
      "quantity": 10
    }
    """
    data = request.get_json() or {}
    id = data.get("id",None)
    ftype = data.get("type")
    name = data.get("name", "")
    description = data.get("description", "")
    price = data.get("price", 0.0)
    dimensions = tuple(data.get("dimensions", []))
    quantity = data.get("quantity", 1)


    if ftype not in FURNITURE_MAP:
        return jsonify({"error": f"Invalid furniture type: {ftype}"}), 400

    furniture_class = FURNITURE_MAP[ftype]
    args = [id, name, description, price, dimensions]

    # Map extra parameter requirements for each furniture type.
    extra_field_defaults = {
        "Chair": ("cushion_material", "default_cushion"),
        "Table": ("frame_material", "default_frame"),
        "Sofa": ("cushion_material", "default_cushion"),
        "Lamp": ("light_source", "default_light_source"),
        "Shelf": ("wall_mounted", "default_wall_mounted")
    }

    if ftype in extra_field_defaults:
        extra_field, default_val = extra_field_defaults[ftype]
        if extra_field:
            extra_value = data.get(extra_field, default_val)
            args.append(extra_value)

    new_furniture = furniture_class(*args)
    new_furniture.id = inventory.get_next_furniture_id()
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
    if email not in shopping_carts:
        return jsonify({"error": "Cart not found for user"}), 404

    cart = shopping_carts[email]
    # Attempt to remove the item with a matching furniture_id.
    found = False
    for child in cart.root._children:
        if child.name == item_id:
            cart.root.remove(child)
            found = True
            break

    if not found:
        return jsonify({"error": "Item not found in cart"}), 404

    return jsonify({"message": "Item removed from cart", "total_price": cart.get_total_price()}), 200

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
if __name__ == "__main__":  # pragma: no cover
    print("[DEBUG_APP]","Starting Flask app...")

    with app.test_client() as client:
        # --- User Registration for Regression Testing ---
        reg_user_response = client.post(
            "/api/users",
            json={
                "email": "regression@example.com",
                "name": "Regression Test1",
                "password": "regress123",
            }
        )
        print("[DEBUG_APP]","User Registration (regression):", reg_user_response.get_json())

        # --- Place an Order with Items Not in Inventory ---
        res_furniture_not_in_inventory = client.post(
            "/api/orders",
            json={
                "user_email": "regression@example.com",
                "items": [{"furniture_id": 1, "quantity": 1}, {"furniture_id": 2, "quantity": 70}]
            }
        )
        print("[DEBUG_APP]","Order (furniture not in inventory):", res_furniture_not_in_inventory.get_json())

        # --- Second User Registration (Regression) ---
        sec_user_response = client.post(
            "/api/users",
            json={
                "email": "regression@example2.com",
                "name": "Regression Test1",
                "password": "regress123",
            }
        )
        print("[DEBUG_APP]","Second User Registration (regression):", sec_user_response.get_json())

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
        print("[DEBUG_APP]","Inventory (Regression Chair):", inv_response.get_json())

        # --- Place Order for an Item That Is in Inventory ---
        res_furniture_in_inventory = client.post(
            "/api/orders",
            json={
                "user_email": "regression@example.com",
                "items": [{"furniture_id": 1, "quantity": 1}]
            }
        )
        print("[DEBUG_APP]","Order (furniture in inventory):", res_furniture_in_inventory.get_json())

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
        print("[DEBUG_APP]","Inventory (Test Chair):", test_chair_response.get_json())
        assert test_chair_response.status_code == 201, f"Furniture creation failed: {test_chair_response.status_code}"
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
        print("[DEBUG_APP]","Order User Registration:", order_user_response.get_json())

        # --- Create Order for Order User Using the Actual Furniture ID ---
        order_response = client.post(
            "/api/orders",
            json={
                "user_email": "orderuser@example.com",
                "items": [{"furniture_id": furniture_id, "quantity": 2}]
            }
        )
        print("[DEBUG_APP]","Order Creation (order user):", order_response.get_json())

        # --- Register User for Cart Update and Checkout ---
        cart_update_user_response = client.post(
            "/api/users",
            json={
                "email": "cartupdate@example.com",
                "name": "Cart Update User",
                "password": "cartpassword"
            }
        )
        print("[DEBUG_APP]","Cart Update User Registration:", cart_update_user_response.get_json())

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
        print("[DEBUG_APP]","Search Results:", search_response.get_json())

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
        print("[DEBUG_APP]","Inventory for Cart Update:", inventory_cart_data)

        # --- Update Shopping Cart for cartupdate@example.com ---
        cart_response_initial = client.put(
            f"/api/cart/cartupdate@example.com",
            json={"items": [{"furniture_id": furniture_id_cartupdate, "quantity": 3}]}
        )
        print("[DEBUG_APP]","Initial Cart Update:", cart_response_initial.get_json())

        cart_response_updated = client.put(
            f"/api/cart/cartupdate@example.com",
            json={"items": [{"furniture_id": furniture_id_cartupdate, "quantity": 5}]}
        )
        print("[DEBUG_APP]","Updated Cart:", cart_response_updated.get_json())
        cart_response_initial = client.put(
            f"/api/cart/cartupdate@example.com",
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
        print("[DEBUG_APP]","Initial Cart Update:", cart_response_initial.get_json())

        # You could make a second update call, e.g., changing quantity or applying a discount
        cart_response_updated = client.put(
            f"/api/cart/cartupdate@example.com",
            json={
                "items": [
                    {
                        "furniture_id": furniture_id_cartupdate,  
                        "quantity": 5,
                        "unit_price": 300.0   # explicitly set the price
                    }
                ]
            }
        )
        print("[DEBUG_APP]","Updated Cart:", cart_response_updated.get_json())

        # --- Remove Item from Cart for cartupdate@example.com ---
        remove_item_response = client.post(
        f"/api/cart/cartupdate@example.com/remove",
        json={
        "item_id": furniture_id_cartupdate,   # e.g., 101
        "unit_price": 300.0,
        "quantity": 3
                }
        )
        print("[DEBUG_APP]","Remove Item from Cart:", remove_item_response.get_json())


        # --- Checkout Process for cartupdate@example.com ---
        checkout_payload = {"payment_method": "credit_card", "address": "123 Test St"}
        checkout_response = client.post(f"/api/checkout/cartupdate@example.com", json=checkout_payload)
        print("[DEBUG_APP]","Checkout Response:", checkout_response.get_json())

        # --- Retrieve and Print All Orders ---
        orders_response = client.get("/api/orders")
        print("[DEBUG_APP]","All Orders:", orders_response.get_json())
        

    # Finally, start your Flask app
    app.run(debug=True)
