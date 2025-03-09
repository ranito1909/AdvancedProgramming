# AdvancedProgrammingProject

## 📌 Group Members
- Ran Bachar
- Itay Yoschpe
- Shahar Hay

## 📖 What’s This Project About?
Welcome to our **Furniture Store API**, built using **Flask** and **Pandas**.  
This project lets users:
- Browse and manage a catalog of furniture items 🛋️
- Register and manage user profiles 👤
- Place and track orders 📦
- Manage shopping carts and checkout 🛒
- Search inventory with advanced filters 🔍

We follow best practices like **object-oriented programming**, **design patterns** (Singleton, Composite, Factory), **type hinting**, and **automated testing** to keep the project clean, consistent, and reliable.

---

## ⚙️ How to Get Started

### 1️⃣ Install Dependencies
Make sure you have Python 3 installed. Then, install the required packages:

    pip install -r requirements.txt

### 2️⃣ Run the API
Start the Flask server by running:

    python app.py

The API will be available at http://127.0.0.1:5000/.

### 3️⃣ Running Tests
To run the test suite and check code coverage, execute:

    pytest --cov=.

---

## 📌 API Overview

### 🛋️ Furniture Endpoints

| Method | Endpoint               | Purpose                                              |
| ------ | ---------------------- | ---------------------------------------------------- |
| GET    | /api/furniture         | Retrieve all furniture items with details and stock |
| POST   | /api/inventory         | Create a new furniture item                          |
| PUT    | /api/inventory/<id>    | Update an existing furniture item                    |
| DELETE | /api/inventory/<id>    | Delete a furniture item                              |

### 👤 User Endpoints

| Method | Endpoint                             | Purpose                                          |
| ------ | ------------------------------------ | ------------------------------------------------ |
| GET    | /api/users                           | Retrieve all registered users                    |
| POST   | /api/users                           | Register a new user                              |
| POST   | /api/users/<email>/profile           | Update a user’s profile (name, address)          |
| PUT    | /api/users/<email>/password          | Update a user’s password                         |
| DELETE | /api/users/<email>                   | Delete a user account                            |
| POST   | /api/login                           | Authenticate a user (login)                      |
| POST   | /api/users/<email>/check_password    | Verify if a provided password is correct         |
| POST   | /api/hash_password                   | Generate a SHA-256 hash for a given password     |

### 📦 Order Endpoints

| Method | Endpoint                        | Purpose                                 |
| ------ | --------------------------------| --------------------------------------- |
| GET    | /api/orders                     | Retrieve all orders                     |
| POST   | /api/orders                     | Place a new order                       |
| GET    | /api/orders/<order_id>/status   | Get the status of a specific order      |
| PUT    | /api/orders/<order_id>/status   | Update the status of an order           |

### 🛒 Shopping Cart Endpoints

| Method | Endpoint                          | Purpose                                                 |
| ------ | --------------------------------- | ------------------------------------------------------- |
| PUT    | /api/cart/<email>                 | Create or update a user’s shopping cart                |
| GET    | /api/cart/<email>/view            | View the contents of a user’s shopping cart            |
| DELETE | /api/cart/<email>/<id>            | Remove a specific item from a shopping cart            |

### 🔒 Checkout Endpoints

| Method | Endpoint                                          | Purpose                                                                       |
| ------ | ------------------------------------------------- | ----------------------------------------------------------------------------- |
| POST   | /api/checkout/<email>                             | Finalize checkout for a user’s cart (requires payment_method and address)     |
| GET    | /api/checkout/<email>/validate                    | Validate if the items in the cart have sufficient inventory                   |
| GET    | /api/checkout/<email>/leaf_items                  | Retrieve the individual leaf items from a user’s shopping cart (debug endpoint) |
| GET    | /api/checkout/<email>/find_furniture?name=...     | Find a furniture item in inventory by its name                                |
| POST   | /api/checkout/<email>/payment                     | Process payment for a user’s shopping cart                                    |

### 🔍 Inventory Search Endpoint

| Method | Endpoint               | Purpose                                                          |
| ------ | ---------------------- | ---------------------------------------------------------------- |
| POST   | /api/inventorysearch   | Search the inventory by name substring, price range, and type   |

---

## 🛠️ Additional Information

- **Data Persistence:** Data is stored in Pandas pickle files located in the `storage/` folder.
- **Design Patterns Used:**
  - **Singleton:** Ensures a single instance of Inventory.
  - **Composite:** Implements ShoppingCart with LeafItem and CompositeItem.
  - **Factory:** Uses FURNITURE_MAP to create furniture objects dynamically.
- **Security:** User passwords are hashed using SHA-256.
- **Testing:** Extensive unit and regression tests ensure functionality and reliability.

🚀 **Let’s Build Something Great!**
