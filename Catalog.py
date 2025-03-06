from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Optional, Type
import hashlib
from enum import Enum
from datetime import datetime
import logging

# Configure logging to report warnings and errors during operations.
logging.basicConfig(level=logging.INFO)

# --------------------------------------------------------------------
# Furniture (Abstract Base Class)
# --------------------------------------------------------------------
class Furniture(ABC):
    """
    An abstract base class representing a piece of furniture.

    Attributes:
        name (str): The furniture name.
        description (str): A short description.
        price (float): The base price before discounts/taxes.
        dimensions (Tuple[float, ...]): Dimensions (e.g., width, depth, height).
    """
    def __init__(self, name: str, description: str, price: float, dimensions: Tuple[float, ...]) -> None:
        self.name = name
        self.description = description
        self.price = price
        self.dimensions = dimensions

    @abstractmethod
    def apply_discount(self, percentage: float) -> None:
        """
        Apply a discount to the price.
        
        :param percentage: Discount percentage (0-100).
        :raises ValueError: If percentage is not within 0-100.
        """
    
    @abstractmethod
    def apply_tax(self, tax_rate: float) -> None:
        """
        Apply a tax to the price.
        
        :param tax_rate: Tax rate as a decimal (e.g., 0.17 for 17%).
        """
    
    @abstractmethod
    def check_availability(self) -> bool:
        """
        Check if this furniture item is available in the inventory.
        
        :return: True if available, False otherwise.
        """
    
    def __str__(self) -> str:
        return f"{self.name} ({self.description}): {self.price:.2f} ₪"

# --------------------------------------------------------------------
# Chair
# --------------------------------------------------------------------
class Chair(Furniture):
    """
    A Chair class with an additional cushion material attribute.

    Attributes:
        cushion_material (str): The material used for the chair's cushion.
    """
    def __init__(self, name: str, description: str, price: float, dimensions: Tuple[float, ...], cushion_material: str) -> None:
        super().__init__(name, description, price, dimensions)
        self.cushion_material = cushion_material

    def apply_discount(self, percentage: float) -> None:
        if not (0 <= percentage <= 100):
            raise ValueError("Discount percentage must be between 0 and 100.")
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= 1 + tax_rate

    def check_availability(self) -> bool:
        # Retrieve the singleton Inventory instance locally to avoid circular dependency.
        inventory = Inventory.get_instance()
        available = inventory.items.get(self, 0) > 0
        if not available:
            logging.warning(f"Chair '{self.name}' is not available in inventory.")
        return available

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Cushion Material: {self.cushion_material}"

# --------------------------------------------------------------------
# Table
# --------------------------------------------------------------------
class Table(Furniture):
    """
    A Table class with a frame material attribute.

    Attributes:
        frame_material (str): The material used for the table frame.
    """
    def __init__(self, name: str, description: str, price: float, dimensions: Tuple[float, ...], frame_material: str) -> None:
        super().__init__(name, description, price, dimensions)
        self.frame_material = frame_material

    def apply_discount(self, percentage: float) -> None:
        if not (0 <= percentage <= 100):
            raise ValueError("Discount percentage must be between 0 and 100.")
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= 1 + tax_rate

    def check_availability(self) -> bool:
        inventory = Inventory.get_instance()
        available = inventory.items.get(self, 0) > 0
        if not available:
            logging.warning(f"Table '{self.name}' is not available in inventory.")
        return available

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Frame Material: {self.frame_material}"

# --------------------------------------------------------------------
# Sofa
# --------------------------------------------------------------------
class Sofa(Furniture):
    """
    A Sofa class with seating capacity information.

    Attributes:
        capacity (int): Number of people who can sit on the sofa.
    """
    def __init__(self, name: str, description: str, price: float, dimensions: Tuple[float, ...], capacity: int) -> None:
        super().__init__(name, description, price, dimensions)
        self.capacity = capacity

    def apply_discount(self, percentage: float) -> None:
        if not (0 <= percentage <= 100):
            raise ValueError("Discount percentage must be between 0 and 100.")
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= 1 + tax_rate

    def check_availability(self) -> bool:
        inventory = Inventory.get_instance()
        available = inventory.items.get(self, 0) > 0
        if not available:
            logging.warning(f"Sofa '{self.name}' is not available in inventory.")
        return available

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Capacity: {self.capacity}"

# --------------------------------------------------------------------
# Lamp
# --------------------------------------------------------------------
class Lamp(Furniture):
    """
    A Lamp class with a specified light source.

    Attributes:
        light_source (str): The type of light (e.g., LED, fluorescent).
    """
    def __init__(self, name: str, description: str, price: float, dimensions: Tuple[float, ...], light_source: str) -> None:
        super().__init__(name, description, price, dimensions)
        self.light_source = light_source

    def apply_discount(self, percentage: float) -> None:
        if not (0 <= percentage <= 100):
            raise ValueError("Discount percentage must be between 0 and 100.")
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= 1 + tax_rate

    def check_availability(self) -> bool:
        inventory = Inventory.get_instance()
        available = inventory.items.get(self, 0) > 0
        if not available:
            logging.warning(f"Lamp '{self.name}' is not available in inventory.")
        return available

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Light Source: {self.light_source}"

# --------------------------------------------------------------------
# Shelf
# --------------------------------------------------------------------
class Shelf(Furniture):
    """
    A Shelf class with an indicator if it is wall-mounted.

    Attributes:
        wall_mounted (bool): True if the shelf is wall-mounted.
    """
    def __init__(self, name: str, description: str, price: float, dimensions: Tuple[float, ...], wall_mounted: bool) -> None:
        super().__init__(name, description, price, dimensions)
        self.wall_mounted = wall_mounted

    def apply_discount(self, percentage: float) -> None:
        if not (0 <= percentage <= 100):
            raise ValueError("Discount percentage must be between 0 and 100.")
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= 1 + tax_rate

    def check_availability(self) -> bool:
        inventory = Inventory.get_instance()
        available = inventory.items.get(self, 0) > 0
        if not available:
            logging.warning(f"Shelf '{self.name}' is not available in inventory.")
        return available

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Wall Mounted: {self.wall_mounted}"

# --------------------------------------------------------------------
# Inventory
# --------------------------------------------------------------------
class Inventory:
    """
    Singleton class managing the furniture inventory.

    Attributes:
        items (Dict[Furniture, int]): A mapping from furniture objects to their available quantity.
    """
    _instance: Optional[Inventory] = None

    def __init__(self) -> None:
        if Inventory._instance is not None:
            raise Exception("Inventory is a singleton. Use Inventory.get_instance() instead.")
        self.items: Dict[Furniture, int] = {}
        Inventory._instance = self

    @staticmethod
    def get_instance() -> Inventory:
        if Inventory._instance is None:
            Inventory()
        return Inventory._instance

    def add_item(self, furniture: Furniture, quantity: int = 1) -> None:
        """
        Add or update a furniture item in the inventory.
        """
        if furniture in self.items:
            self.items[furniture] += quantity
        else:
            self.items[furniture] = quantity

    def remove_item(self, furniture: Furniture, quantity: int = 1) -> bool:
        """
        Remove a given quantity of a furniture item.
        
        :return: True if removal succeeded, otherwise False.
        """
        if furniture not in self.items:
            logging.error(f"Attempted to remove non-existent item: {furniture.name}")
            return False
        if self.items[furniture] < quantity:
            logging.error(f"Not enough quantity of {furniture.name} to remove.")
            return False
        self.items[furniture] -= quantity
        if self.items[furniture] <= 0:
            del self.items[furniture]
        return True

    def update_quantity(self, furniture: Furniture, new_quantity: int) -> bool:
        """
        Update the quantity of a specific furniture item.
        
        :return: True if update succeeded, False otherwise.
        """
        if furniture not in self.items:
            logging.error(f"Item {furniture.name} not found during update.")
            return False
        if new_quantity <= 0:
            del self.items[furniture]
        else:
            self.items[furniture] = new_quantity
        return True

    def search(
        self,
        name_substring: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        furniture_type: Optional[Type] = None,
    ) -> List[Furniture]:
        """
        Search for furniture matching the given criteria.
        
        :return: A list of matching furniture items.
        """
        results: List[Furniture] = []
        for item in self.items.keys():
            if name_substring and name_substring.lower() not in item.name.lower():
                continue
            if min_price is not None and item.price < min_price:
                continue
            if max_price is not None and item.price > max_price:
                continue
            results.append(item)
        return results

    def get_quantity(self, furniture: Furniture) -> int:
        """
        Get the current quantity of a specific furniture item.
        """
        return self.items.get(furniture, 0)

# --------------------------------------------------------------------
# User
# --------------------------------------------------------------------
class User:
    """
    Represents a user in the system with authentication and profile management.

    Attributes:
        name (str): User's name.
        email (str): User's unique email address.
        password_hash (str): SHA-256 hash of the user's password.
        address (str): User's address.
        order_history (List[str]): History of the user's orders.
    """
    _users: Dict[str, User] = {}

    def __init__(self, name: str, email: str, password_hash: str, address: str = "", order_history: Optional[List[str]] = None) -> None:
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.address = address
        self.order_history = order_history if order_history is not None else []

    @classmethod
    def register_user(cls, name: str, email: str, raw_password: str, address: str = "") -> User:
        if email in cls._users:
            raise ValueError(f"User with email '{email}' already exists.")
        password_hash = cls._hash_password(raw_password)
        user = cls(name, email, password_hash, address)
        cls._users[email] = user
        return user

    @classmethod
    def login_user(cls, email: str, raw_password: str) -> Optional[User]:
        user = cls._users.get(email)
        if user and user.check_password(raw_password):
            return user
        return None

    @classmethod
    def get_user(cls, email: str) -> Optional[User]:
        return cls._users.get(email)

    @classmethod
    def delete_user(cls, email: str) -> bool:
        if email in cls._users:
            del cls._users[email]
            return True
        return False

    def set_password(self, raw_password: str) -> None:
        self.password_hash = self._hash_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return self._hash_password(raw_password) == self.password_hash

    def update_profile(self, name: Optional[str] = None, address: Optional[str] = None) -> None:
        if name:
            self.name = name
        if address:
            self.address = address

    def add_order(self, order_info: str) -> None:
        self.order_history.append(order_info)

    @staticmethod
    def _hash_password(raw_password: str) -> str:
        return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()

# --------------------------------------------------------------------
# CartComponent (Abstract Base Class)
# --------------------------------------------------------------------
class CartComponent(ABC):
    """
    Abstract base class for items in the shopping cart.
    """
    @abstractmethod
    def get_price(self) -> float:
        """
        Return the total price for this component.
        """

    @abstractmethod
    def apply_discount(self, percentage: float) -> None:
        """
        Apply a discount to this component.
        """
    
    def add(self, component: CartComponent) -> None:
        raise NotImplementedError("This component does not support adding children.")

    def remove(self, component: CartComponent) -> None:
        raise NotImplementedError("This component does not support removing children.")

# --------------------------------------------------------------------
# LeafItem
# --------------------------------------------------------------------
class LeafItem(CartComponent):
    """
    Represents a single item (leaf) in the shopping cart.

    Attributes:
        name (str): The item name.
        unit_price (float): Price per unit.
        quantity (int): Number of units.
    """
    def __init__(self, name: str, unit_price: float, quantity: int = 1) -> None:
        self.name = name
        self.unit_price = unit_price
        self.quantity = quantity
        self._current_price = unit_price  # Tracks price after discount

    def get_price(self) -> float:
        return self._current_price * self.quantity

    def apply_discount(self, percentage: float) -> None:
        if not (0 <= percentage <= 100):
            raise ValueError("Discount percentage must be between 0 and 100.")
        discount_amount = self.unit_price * (percentage / 100)
        self._current_price = self.unit_price - discount_amount

    def __str__(self) -> str:
        return f"LeafItem({self.name}, Price={self.unit_price:.2f}, Qty={self.quantity})"

# --------------------------------------------------------------------
# CompositeItem
# --------------------------------------------------------------------
class CompositeItem(CartComponent):
    """
    Represents a composite item (bundle) that contains multiple CartComponents.
    """
    def __init__(self, name: str) -> None:
        self.name = name
        self._children: List[CartComponent] = []

    def add(self, component: CartComponent) -> None:
        self._children.append(component)

    def remove(self, component: CartComponent) -> None:
        self._children.remove(component)

    def get_price(self) -> float:
        return sum(child.get_price() for child in self._children)

    def apply_discount(self, percentage: float) -> None:
        for child in self._children:
            child.apply_discount(percentage)

    def __str__(self) -> str:
        return f"CompositeItem({self.name}, children={len(self._children)})"

# --------------------------------------------------------------------
# ShoppingCart
# --------------------------------------------------------------------
class ShoppingCart:
    """
    Implements a shopping cart using the Composite design pattern.
    """
    def __init__(self, name: str = "ShoppingCart") -> None:
        self.root = CompositeItem(name=name)

    def add_item(self, item: CartComponent) -> None:
        self.root.add(item)

    def remove_item(self, item: CartComponent) -> None:
        self.root.remove(item)

    def get_total_price(self) -> float:
        return self.root.get_price()

    def apply_discount(self, percentage: float, target: Optional[CartComponent] = None) -> None:
        if target:
            target.apply_discount(percentage)
        else:
            self.root.apply_discount(percentage)

    def view_cart(self) -> str:
        if not self.root._children:
            return "Shopping cart is empty."
        lines = [f"Cart '{self.root.name}' contents:\n"]
        for component in self.root._children:
            lines.append(f"- Item: {component}, Price: {component.get_price():.2f}")
        lines.append(f"\nTotal price: {self.get_total_price():.2f}")
        return "\n".join(lines)

# --------------------------------------------------------------------
# Checkout
# --------------------------------------------------------------------
class Checkout:
    """
    Manages the checkout process: validating cart, processing payment, finalizing orders.
    """
    def __init__(self, user: User, cart: ShoppingCart, inventory: Inventory) -> None:
        self.user = user
        self.cart = cart
        self.inventory = inventory
        self.payment_method: Optional[str] = None
        self.address: Optional[str] = None
        self.order_finalized: bool = False

    def set_payment_method(self, method: str) -> None:
        self.payment_method = method

    def set_address(self, address: str) -> None:
        self.address = address

    def validate_cart(self) -> bool:
        leaf_items = self._collect_leaf_items(self.cart.root)
        for item in leaf_items:
            furniture_in_inventory = self._find_furniture_by_name(item.name)
            if not furniture_in_inventory:
                logging.error(f"Furniture '{item.name}' not found during checkout.")
                return False
            required_qty = item.quantity
            available_qty = self.inventory.get_quantity(furniture_in_inventory)
            if required_qty > available_qty:
                logging.error(f"Not enough '{item.name}': required {required_qty}, available {available_qty}.")
                return False
        return True

    def process_payment(self) -> bool:
        if not self.payment_method:
            logging.error("Payment method not set.")
            return False
        # Mock payment processing
        return True

    def finalize_order(self) -> bool:
        if self.order_finalized:
            logging.error("Order already finalized.")
            return False
        if not self.validate_cart():
            logging.error("Cart validation failed during checkout.")
            return False
        if not self.process_payment():
            logging.error("Payment processing failed.")
            return False

        leaf_items = self._collect_leaf_items(self.cart.root)
        for item in leaf_items:
            furniture_in_inventory = self._find_furniture_by_name(item.name)
            if furniture_in_inventory:
                self.inventory.remove_item(furniture_in_inventory, item.quantity)

        self.order_summary = (
            f"Order for {self.user.name}, "
            f"Items: {[f'{i.name} x {i.quantity}' for i in leaf_items]}, "
            f"Ship to: {self.address}, "
            f"Payment via: {self.payment_method}, "
            f"Total: {self.cart.get_total_price():.2f}"
        )
        self.user.add_order(self.order_summary)
        self.order_finalized = True
        return True

    def _collect_leaf_items(self, component: CartComponent) -> List[LeafItem]:
        if isinstance(component, LeafItem):
            return [component]
        if isinstance(component, CompositeItem):
            result: List[LeafItem] = []
            for child in component._children:
                result.extend(self._collect_leaf_items(child))
            return result
        return []

    def _find_furniture_by_name(self, name: str) -> Optional[Furniture]:
        """
        First, attempt to convert the LeafItem name to an integer to match by id.
        If conversion fails, fall back to matching by the furniture's name.
        """
        # Try matching by id if the name is numeric.
        try:
            target_id = int(name)
            for furniture_item in self.inventory.items.keys():
                if hasattr(furniture_item, "id") and furniture_item.id == target_id:
                    return furniture_item
        except ValueError:
            pass  # Not an integer, proceed to match by name.

        # Fallback: match by furniture name.
        for furniture_item in self.inventory.items.keys():
            if hasattr(furniture_item, "name") and furniture_item.name == name:
                return furniture_item
        return None

# --------------------------------------------------------------------
# OrderStatus (Enum)
# --------------------------------------------------------------------
class OrderStatus(Enum):
    """
    Enum representing possible order statuses.
    """
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"

# --------------------------------------------------------------------
# Order
# --------------------------------------------------------------------
class Order:
    """
    Represents an order placed by a user.

    Attributes:
        user (User): The user who placed the order.
        items (List[LeafItem]): List of purchased items.
        total_price (float): Total cost at checkout.
        status (OrderStatus): Current order status.
        created_at (datetime): Timestamp when the order was created.
    """
    all_orders = []  # Class-level list to store all orders.

    def __init__(self, user: User, items: List[LeafItem], total_price: float, status: OrderStatus = OrderStatus.PENDING) -> None:
        self.user = user
        self.items = items
        self.total_price = total_price
        self.status = status
        self.created_at = datetime.now()
        self.order_id = len(Order.all_orders) + 1  # Assign an order id.
        Order.all_orders.append(self)

    def set_status(self, new_status: OrderStatus) -> None:
        self.status = new_status

    def get_status(self) -> OrderStatus:
        return self.status
    
    def to_dict(self) -> dict:
        """
        Convert this Order instance to a dictionary.
        """
        return {
            "order_id": self.order_id,
            "user_email": self.user.email,
            "items": [
                {"name": item.name, "quantity": item.quantity, "unit_price": item.unit_price}
                for item in self.items
            ],
            "total_price": self.total_price,
            "status": self.status.value,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __str__(self) -> str:
        item_descriptions = ", ".join(f"{i.name} x {i.quantity}" for i in self.items)
        return (
            f"Order for {self.user.name} | Status: {self.status.value}\n"
            f"Items: {item_descriptions}\n"
            f"Total Price: {self.total_price:.2f}\n"
            f"Created at: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )