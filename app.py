from flask import Flask, request, jsonify
import os
from typing import Union, Dict, List
import pandas as pd
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

def safe_load_pickle(file_path: str, default_df: pd.DataFrame) -> pd.DataFrame:
    """
    Safely load a pickle file containing a pandas DataFrame.

    If the file does not exist, is empty, or contains invalid data, it resets the file with default_df.
    
    Args:
        file_path (str): The path to the pickle file.
        default_df (pd.DataFrame): The default DataFrame to use if loading fails.
    
    Returns:
        pd.DataFrame: The loaded or default DataFrame.
    """
    try:
        df = pd.read_pickle(file_path)
        if not isinstance(df, pd.DataFrame):  # Ensure it's a DataFrame
            raise ValueError("Invalid pickle content, resetting file.")
        return df
    except (EOFError, FileNotFoundError, ValueError, pickle.UnpicklingError):
        with open(file_path, "wb") as f:
            pickle.dump(default_df, f)
        return default_df

# Load data with error handling
orders_df = safe_load_pickle(os.path.join(storage_dir, "orders.pkl"), files_with_defaults["orders.pkl"])
users_df = safe_load_pickle(os.path.join(storage_dir, "users.pkl"), files_with_defaults["users.pkl"])
cart_df = safe_load_pickle(os.path.join(storage_dir, "cart.pkl"), files_with_defaults["cart.pkl"])
furniture_df = safe_load_pickle(os.path.join(storage_dir, "inventory.pkl"), files_with_defaults["inventory.pkl"])


# Initialize the Inventory singleton
inventory: Inventory = Inventory.get_instance()
shopping_carts: Dict[str, ShoppingCart] = {}

def custom_append(self, other: Union[Dict, List], ignore_index: bool = False) -> pd.DataFrame:
    """
    Custom implementation for DataFrame.append to support dictionaries and lists.

    Converts the input to a DataFrame if necessary, then concatenates it to self.
    
    Args:
        other (dict or list): The data to append.
        ignore_index (bool): Whether to ignore the index during concatenation.
    
    Returns:
        pd.DataFrame: The concatenated DataFrame.
    """
    if isinstance(other, dict):
        other = pd.DataFrame([other])
    elif isinstance(other, list):
        other = pd.DataFrame(other)
    return pd.concat([self, other], ignore_index=ignore_index)

pd.DataFrame.append = custom_append


app = Flask(__name__)


def save_orders(orders_df: pd.DataFrame, filename: str = "orders.pkl", storage_dir: str = "storage") -> None:
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

def save_users(users_dict: Dict[str, User], filename: str = "users.pkl", storage_dir: str = "storage") -> None:
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

def save_cart(shopping_carts: Dict[str, ShoppingCart], filename: str = "cart.pkl", storage_dir: str = "storage") ->None:
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

def save_inventory(inventory_instance: inventory, filename: str = "inventory.pkl", storage_dir: str = "storage") -> pd.DataFrame:
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
    """
    Retrieve all orders.
    
    Returns a JSON list of all orders stored in Order.all_orders.
    """
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
    """
    Locate a furniture item in the inventory by its unique ID.
    
    Args:
        furniture_id (int): The ID of the furniture item.
    
    Returns:
        The furniture item if found; otherwise, None.
    """
    return next((item for item in inventory.items.keys() if getattr(item, "id", None) == furniture_id), None)

@app.route("/api/inventory/<int:furniture_id>/quantity", methods=["GET"])
def get_quantity_for_item(furniture_id: int):
    """
    Retrieve the available quantity for a specific furniture item by its ID.
    
    This endpoint uses the Inventory.get_quantity() method defined in Catalog.py.
    """
    furniture_item = get_furniture_item_by_id(furniture_id)
    if not furniture_item:
        return jsonify({"error": "Furniture item not found"}), 404

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

@app.route("/api/orders/<int:order_id>/status", methods=["GET"])
def get_order_status(order_id: int):
    """
    Retrieve the status of an order by its ID.
    
    Args:
        order_id (int): The unique identifier for the order.
    
    Returns:
        A JSON object containing the order_id and its status.
    """
    # Find the order by ID
    order = next((o for o in Order.all_orders if o.order_id == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    return jsonify({"order_id": order.order_id, "status": order.get_status().value}), 200

@app.route("/api/users/<string:email>/order_history", methods=["GET"])
def get_user_order_history(email: str):
    """
    Retrieve the order history for the specified user.

    Returns:
        JSON object with the user's email and their order history,
        or an error if the user is not found.
    """
    user = User.get_user(email)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"email": user.email, "order_history": user.get_order_history()}), 200



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



    # Run the inventory search
    inventory = Inventory.get_instance()
    search_results = inventory.search(
        name_substring=name_substring,
        min_price=min_price,
        max_price=max_price,
        furniture_type=furniture_type_str,
    )

    # Convert results to a list of dicts if needed or return them directly if they are JSON serializable
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
    """
    Authenticate a user and return user details if the credentials are valid.
    
    Expects a JSON payload with 'email' and 'password'. Returns an error if authentication fails.
    """
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
def check_password(email: str):
    """
    Verify whether the provided password matches the stored password for a user.
    
    Args:
        email (str): The email of the user.
    
    Returns:
        A JSON object with a boolean indicating if the password is correct.
    """
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
    """
    Generate a SHA-256 hash for the provided password.
    
    Expects a JSON payload with 'password' and returns the hashed password.
    """
    data = request.get_json() or {}
    raw_password = data.get("password")
    if not raw_password:
        return jsonify({"error": "Missing password"}), 400
    hashed = User._hash_password(raw_password)
    return jsonify({"hashed_password": hashed}), 200

@app.route("/api/orders", methods=["POST"])
def create_order():
    """
    Create a new order based on the provided user email and order items.
    
    Validates inventory availability, creates an order, updates inventory and the user's order history,
    and returns the created order details.
    """
    data = request.get_json() or {}
    user_email = data.get("user_email")
    
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
            if getattr(furniture, "id", None) == furniture_id:
                if not furniture.check_availability(): # Ensure no zero-quantity items
                    return jsonify({"error": f"Furniture '{furniture.name}' is not available"}), 400
                if inventory.items[furniture] < order_quantity:
                    return jsonify({"error": f"Not enough quantity for furniture with id {furniture_id}"}), 400
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
def update_profile(email: str):
    """
    Update an existing user's profile.
    """
    data = request.get_json() or {}
    user = User.get_user(email)
    if not user:
        return jsonify({"message": "No such user"}), 200

    user.update_profile(name=data.get("name"), address=data.get("address"))
    return jsonify({
        "email": user.email,
        "name": user.name,
        "password_hash": user.password_hash,
        "address": user.address,
        "order_history": user.order_history
    }), 200

@app.route("/api/checkout/<email>", methods=["POST"])
def checkout(email: str):
    """
    Process the checkout for a user's shopping cart.
    
    Expects a JSON payload with 'payment_method' and 'address'. Validates the cart,
    finalizes the order, updates the user's order history, and returns an order summary.
    """
    data = request.get_json() or {}

    payment_method = data.get("payment_method")
    address = data.get("address")
    if not payment_method or not address:
        return jsonify({"error": "Both payment_method and address are required."}), 400

    if email not in shopping_carts:
        return jsonify({"error": "Shopping cart not found for user."}), 404
    if email not in User._users:
        return jsonify({"error": "User not found."}), 404

    cart = shopping_carts[email]
    user = User._users[email]
    
    checkout_obj = Checkout(user, cart, inventory)
    checkout_obj.set_payment_method(payment_method)
    checkout_obj.set_address(address)

    if not checkout_obj.finalize_order():
        return jsonify({"error": "Checkout process failed. Check logs for details."}), 400

    # Assuming the user object stores order summaries in an 'orders' list.
    order_summary = checkout_obj.order_summary or "Order summary not available"
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
    payment_result = checkout_obj.process_payment()
    if payment_result:
        return jsonify({"payment_success": True}), 200
    else:
        return jsonify({"payment_success": False, "error": "Payment processing failed"}), 400

# ---------------------------
# PUT Endpoints
# ---------------------------
@app.route("/api/cart/<email>", methods=["PUT"])
def update_cart(email: str):
    """
    Update or create the shopping cart for the specified user.

    Expects a JSON payload with a list of items. If a cart already exists, it clears previous items;
    otherwise, it creates a new ShoppingCart. Each item is processed (including discount application)
    and added to the cart. Returns the updated cart details including user_email, list of items, and total price.
    """
    data = request.get_json() or {}
    
    items = data.get("items", [])
    if not isinstance(items, list):
        return jsonify({"error": "items must be a list"}), 400

    if email in shopping_carts:
        cart = shopping_carts[email]
    else:
        cart = ShoppingCart(name=email)
        shopping_carts[email] = cart

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

    total_price = cart.get_total_price()
    response_items = []
    for child in cart.root._children:
        response_items.append({
            "furniture_id": int(child.name),
            "quantity": child.quantity
        })

    return jsonify({"user_email": email, "items": response_items, "total_price": total_price}), 200


@app.route("/api/inventory/<int:furniture_id>", methods=["PUT"])
def update_inventory(furniture_id: int):
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
def update_password(email: str):
    """
    Update the password for a user.
    
    Expects a JSON payload with 'new_password' and updates the user's password if the user exists.
    """
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
def update_order_status(order_id: int):
    """
    Update the status of an order.
    
    Expects a JSON payload with 'status' and updates the order's status if the order exists.
    """
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
    {
      "class": "Chair" or "Table" or "Sofa" or "Lamp" or "Shelf",
      "name": "...",
      "description": "...",
      "price": 123.45,
      "dimensions": [width, depth, height],
      "quantity": 10
    }
    """
    data = request.get_json() or {}
    id = None  # Placeholder for the ID, which is generated by the Inventory.
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
def delete_inventory(furniture_id: int):
    """
    Delete a furniture item from the inventory.
    
    Searches for the furniture item by its ID and removes it if found, then updates the inventory persistence.
    """
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
def delete_cart_item(email: str, item_id: int):
    """
    Remove an item from a user's shopping cart.

    Searches for an item in the specified user's cart by matching the item_id.
    If found, the item is removed and the updated total cart price is returned.
    If not found, an error message is returned.
    """
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
def delete_user(email: str):
    """
    Delete a user via the User.delete_user class method.
    """
    if not User.delete_user(email):
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User deleted"}), 200


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True)
