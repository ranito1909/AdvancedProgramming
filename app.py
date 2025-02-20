from flask import Flask, request, jsonify
import pandas as pd
import os
import hashlib

app = Flask(__name__)

# --------------------------------------------------------------------
# File names for persistence using pandas pickle
# --------------------------------------------------------------------
FURNITURE_FILE = 'furniture.pkl'
ORDERS_FILE = 'orders.pkl'
USERS_FILE = 'users.pkl'
CART_FILE = 'cart.pkl'

# --------------------------------------------------------------------
# Load or initialize DataFrames
# --------------------------------------------------------------------
if os.path.exists(FURNITURE_FILE):
    furniture_df = pd.read_pickle(FURNITURE_FILE)
else:
    furniture_df = pd.DataFrame(columns=['id', 'name', 'description', 'price', 'dimensions'])

if os.path.exists(ORDERS_FILE):
    orders_df = pd.read_pickle(ORDERS_FILE)
else:
    orders_df = pd.DataFrame(columns=['order_id', 'user_email', 'items', 'total'])

if os.path.exists(USERS_FILE):
    users_df = pd.read_pickle(USERS_FILE)
else:
    users_df = pd.DataFrame(columns=['email', 'name', 'password_hash', 'address', 'order_history'])

if os.path.exists(CART_FILE):
    cart_df = pd.read_pickle(CART_FILE)
else:
    cart_df = pd.DataFrame(columns=['user_email', 'items'])


# --------------------------------------------------------------------
# Helper functions to save DataFrames to pickle files
# --------------------------------------------------------------------
def save_furniture():
    global furniture_df
    furniture_df.to_pickle(FURNITURE_FILE)


def save_orders():
    global orders_df
    orders_df.to_pickle(ORDERS_FILE)


def save_users():
    global users_df
    users_df.to_pickle(USERS_FILE)


def save_cart():
    global cart_df
    cart_df.to_pickle(CART_FILE)


# --------------------------------------------------------------------
# GET endpoints
# --------------------------------------------------------------------
@app.route('/api/furniture', methods=['GET'])
def get_furniture():
    global furniture_df
    return furniture_df.to_json(orient='records'), 200


@app.route('/api/orders', methods=['GET'])
def get_orders():
    global orders_df
    return orders_df.to_json(orient='records'), 200


@app.route('/api/users', methods=['GET'])
def get_users():
    global users_df
    return users_df.to_json(orient='records'), 200


# --------------------------------------------------------------------
# POST endpoints
# --------------------------------------------------------------------
@app.route('/api/users', methods=['POST'])
def register_user():
    global users_df
    data = request.get_json()
    email = data.get('email')
    if email in users_df['email'].values:
        return jsonify({'error': 'User already exists'}), 400

    password = data.get('password')
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    name = data.get('name')
    address = data.get('address', '')
    new_user = {
        'email': email,
        'name': name,
        'password_hash': password_hash,
        'address': address,
        'order_history': []
    }
    users_df = users_df.append(new_user, ignore_index=True)
    save_users()
    return jsonify(new_user), 201


@app.route('/api/orders', methods=['POST'])
def create_order():
    global orders_df, users_df
    data = request.get_json()
    order_id = data.get('order_id', len(orders_df) + 1)
    user_email = data.get('user_email')
    items = data.get('items')
    total = data.get('total')
    new_order = {
        'order_id': order_id,
        'user_email': user_email,
        'items': items,
        'total': total
    }
    orders_df = orders_df.append(new_order, ignore_index=True)
    save_orders()

    # Update user's order history
    if user_email in users_df['email'].values:
        idx = users_df.index[users_df['email'] == user_email].tolist()[0]
        history = users_df.at[idx, 'order_history']
        if not isinstance(history, list):
            history = []
        history.append(new_order)
        users_df.at[idx, 'order_history'] = history
        save_users()

    return jsonify(new_order), 201


@app.route('/api/users/<email>/profile', methods=['POST'])
def update_profile(email):
    global users_df
    data = request.get_json()
    if email not in users_df['email'].values:
        return jsonify({'error': 'User not found'}), 404
    idx = users_df.index[users_df['email'] == email].tolist()[0]
    name = data.get('name')
    address = data.get('address')
    if name:
        users_df.at[idx, 'name'] = name
    if address:
        users_df.at[idx, 'address'] = address
    save_users()
    return jsonify(users_df.loc[idx].to_dict()), 200


# --------------------------------------------------------------------
# PUT endpoints for updating cart and inventory
# --------------------------------------------------------------------
@app.route('/api/cart/<email>', methods=['PUT'])
def update_cart(email):
    global cart_df
    data = request.get_json()
    items = data.get('items')
    if email in cart_df['user_email'].values:
        idx = cart_df.index[cart_df['user_email'] == email].tolist()[0]
        cart_df.at[idx, 'items'] = items
    else:
        new_cart = {'user_email': email, 'items': items}
        cart_df = cart_df.append(new_cart, ignore_index=True)
    save_cart()
    return jsonify({'user_email': email, 'items': items}), 200


@app.route('/api/inventory/<int:furniture_id>', methods=['PUT'])
def update_inventory(furniture_id):
    global furniture_df
    data = request.get_json()
    if furniture_id not in furniture_df['id'].values:
        return jsonify({'error': 'Furniture item not found'}), 404
    idx = furniture_df.index[furniture_df['id'] == furniture_id].tolist()[0]
    for key, value in data.items():
        if key in furniture_df.columns:
            furniture_df.at[idx, key] = value
    save_furniture()
    return jsonify(furniture_df.loc[idx].to_dict()), 200


# --------------------------------------------------------------------
# DELETE endpoints for cart and inventory
# --------------------------------------------------------------------
@app.route('/api/cart/<email>/<item_id>', methods=['DELETE'])
def delete_cart_item(email, item_id):
    global cart_df
    if email not in cart_df['user_email'].values:
        return jsonify({'error': 'Cart not found for user'}), 404
    idx = cart_df.index[cart_df['user_email'] == email].tolist()[0]
    items = cart_df.at[idx, 'items']
    new_items = [item for item in items if str(item.get('furniture_id')) != item_id]
    if len(new_items) == len(items):
        return jsonify({'error': 'Item not found in cart'}), 404
    cart_df.at[idx, 'items'] = new_items
    save_cart()
    return jsonify({'message': 'Item removed from cart'}), 200


@app.route('/api/inventory/<int:furniture_id>', methods=['DELETE'])
def delete_inventory(furniture_id):
    global furniture_df
    if furniture_id not in furniture_df['id'].values:
        return jsonify({'error': 'Furniture item not found'}), 404
    furniture_df.drop(furniture_df.index[furniture_df['id'] == furniture_id], inplace=True)
    save_furniture()
    return jsonify({'message': 'Furniture item deleted'}), 200


# --------------------------------------------------------------------
# Run the Flask application
# --------------------------------------------------------------------
if __name__ == '__main__':
    print("staring the app")
    app.run(debug=True)
