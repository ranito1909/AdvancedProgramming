# AdvancedProgrammingProject

## 📌 Group Members
- Ran Bachar
- Itay Yoschpe
- Shahar Hay

## 📖 What’s This Project About?

Welcome to our **Furniture Store API**, built using **Flask** and **Pandas**. 
This project lets users:

- Browse and manage a catalog of furniture items 🛋️
- Create and manage user profiles 👤
- Place and track orders 📦
- Handle shopping carts 🛒

We follow best practices like **type hinting**, **code documentation**, and **automated testing** to keep things clean and reliable!

---

## ⚙️ How to Get Started

### **1️⃣ Install the Necessary Dependencies**

Make sure you have Python 3 installed. Then, install the required packages:

```bash
pip install -r requirements.txt
```

### **2️⃣ Run the API**

Start the Flask server by running:

```bash
python app.py
```

### **3️⃣ Access the API**

Once running, you can interact with the API at `http://127.0.0.1:5000/`.

---

## 📌 API Overview

### **Furniture Routes**

| Method | Endpoint              | Purpose                   |
| ------ | --------------------- | ------------------------- |
| GET    | `/api/furniture`      | Get all furniture items   |
| PUT    | `/api/inventory/<id>` | Update a furniture item   |
| DELETE | `/api/inventory/<id>` | Remove a furniture item   |

### **User Routes**

| Method | Endpoint                     | Purpose                |
| ------ | ---------------------------- | ---------------------- |
| GET    | `/api/users`                 | Get all users          |
| POST   | `/api/users`                 | Register a new user    |
| POST   | `/api/users/<email>/profile` | Update a user profile  |
| DELETE | `/api/users/<email>`         | Delete a user account  |

### **Order Routes**

| Method | Endpoint      | Purpose                 |
| ------ | ------------ | ----------------------- |
| GET    | `/api/orders` | View all orders        |
| POST   | `/api/orders` | Place a new order      |

### **Shopping Cart Routes**

| Method | Endpoint                 | Purpose                  |
| ------ | ------------------------ | ------------------------ |
| PUT    | `/api/cart/<email>`      | Update a user's cart     |
| DELETE | `/api/cart/<email>/<id>` | Remove an item from cart |

---

## 🛠️ Running Tests

To check if everything is working, run:

```bash
pytest --cov=.
```

This will test all API routes and ensure business logic is solid. ✅

---

## 📝 Extra Info

- Data is stored using **Pandas pickle files** 📂.
- The inventory and shopping cart are built with **object-oriented programming** 🏗️.
- User passwords are stored securely using **hashed passwords** 🔒.

🚀 **Let’s Build Something Great!**

