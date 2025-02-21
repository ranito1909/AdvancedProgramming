### Part 1 ###

from abc import ABC, abstractmethod
from typing import Tuple


# --------------------------------------------------------------------
# Furniture (Abstract Base Class)
# --------------------------------------------------------------------
class Furniture(ABC):
    """
    An abstract base class that represents a general piece of furniture.
    """

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        dimensions: Tuple[float, ...]
    ):
        """
        Initialize a piece of furniture.

        :param name: The name of the furniture.
        :param description: A short description of the furniture.
        :param price: The base price of the furniture (before any discounts/taxes).
        :param dimensions: A tuple representing the dimensions of the furniture 
                           (e.g., width, depth, height).
        """
        self.name = name
        self.description = description
        self.price = price
        self.dimensions = dimensions

    @abstractmethod
    def apply_discount(self, percentage: float) -> None:
        """
        Apply a discount to the price. 
        The percentage parameter is a number between 0 and 100.
        """
        pass

    @abstractmethod
    def apply_tax(self, tax_rate: float) -> None:
        """
        Apply a tax (e.g., VAT) to the price. 
        For instance, a tax_rate of 0.17 represents 17% tax.
        """
        pass

    @abstractmethod
    def check_availability(self) -> bool:
        """
        Check if this piece of furniture is in stock. 
        For now, return True or False as a placeholder.
        """
        pass

    def __str__(self) -> str:
        return f"{self.name} ({self.description}): {self.price:.2f} ₪"


# --------------------------------------------------------------------
# Chair
# --------------------------------------------------------------------
class Chair(Furniture):
    """
    A Chair class, representing a chair with a specific cushion material.

    Attributes:
        cushion_material (str): The type of material used for the seat cushion.
    """

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        dimensions: Tuple[float, ...],
        cushion_material: str
    ):
        super().__init__(name, description, price, dimensions)
        self.cushion_material = cushion_material

    def apply_discount(self, percentage: float) -> None:
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= (1 + tax_rate)

    def check_availability(self) -> bool:
        # Temporary implementation returning True; 
        # will be extended in the future with actual inventory checks.
        return True

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Cushion Material: {self.cushion_material}"


# --------------------------------------------------------------------
# Table
# --------------------------------------------------------------------
class Table(Furniture):
    """
    A Table class, representing a table with a specific frame material.

    Attributes:
        frame_material (str): The type of material used for the table frame.
    """

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        dimensions: Tuple[float, ...],
        frame_material: str
    ):
        super().__init__(name, description, price, dimensions)
        self.frame_material = frame_material

    def apply_discount(self, percentage: float) -> None:
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= (1 + tax_rate)

    def check_availability(self) -> bool:
        # Temporary implementation returning True.
        return True

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Frame Material: {self.frame_material}"


# --------------------------------------------------------------------
# Sofa
# --------------------------------------------------------------------
class Sofa(Furniture):
    """
    A Sofa class, representing a sofa with a seating capacity.

    Attributes:
        capacity (int): Number of people who can sit on the sofa.
    """

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        dimensions: Tuple[float, ...],
        capacity: int
    ):
        super().__init__(name, description, price, dimensions)
        self.capacity = capacity

    def apply_discount(self, percentage: float) -> None:
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= (1 + tax_rate)

    def check_availability(self) -> bool:
        # Temporary implementation returning True.
        return True

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Capacity: {self.capacity}"


# --------------------------------------------------------------------
# Lamp
# --------------------------------------------------------------------
class Lamp(Furniture):
    """
    A Lamp class, representing a lamp with a specific light source type.

    Attributes:
        light_source (str): The type of light emitted by the lamp.
    """

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        dimensions: Tuple[float, ...],
        light_source: str
    ):
        super().__init__(name, description, price, dimensions)
        self.light_source = light_source

    def apply_discount(self, percentage: float) -> None:
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= (1 + tax_rate)

    def check_availability(self) -> bool:
        # Temporary implementation returning True.
        return True

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Light Source: {self.light_source}"


# --------------------------------------------------------------------
# Shelf
# --------------------------------------------------------------------
class Shelf(Furniture):
    """
    A Shelf class, representing a shelf that may or may not be wall-mounted.

    Attributes:
        wall_mounted (bool): Indicates whether the shelf is wall-mounted.
    """

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        dimensions: Tuple[float, ...],
        wall_mounted: bool
    ):
        super().__init__(name, description, price, dimensions)
        self.wall_mounted = wall_mounted

    def apply_discount(self, percentage: float) -> None:
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= (1 + tax_rate)

    def check_availability(self) -> bool:
        # Temporary implementation returning True.
        return True

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Wall Mounted: {self.wall_mounted}"
    


### PART 2 ###

from typing import Dict, List
from furniture import Furniture, Chair, Table, Sofa, Lamp, Shelf


class Inventory:
    """
    A Singleton class that manages an inventory of furniture.
    Only one instance of this class can exist.
    """

    _instance = None  # Static variable to hold the single instance of the class

    def __init__(self):
        """
        Initialize the data structure for the inventory:
        - items: a dictionary mapping a Furniture object to the quantity in stock.
        """
        if Inventory._instance is not None:
            # Prevent creating another instance of a Singleton
            raise Exception(
                "Inventory is a singleton class. Use Inventory.get_instance() instead."
            )
        self.items: Dict[Furniture, int] = {}
        Inventory._instance = self

    @staticmethod
    def get_instance():
        """
        Return the existing instance of the class or create a new one if it doesn't exist.
        """
        if Inventory._instance is None:
            Inventory()
        return Inventory._instance

    # ----------------------------------------------------------------
    # Add, Remove and Update quantity Operations
    # ----------------------------------------------------------------

    def add_item(self, furniture: Furniture, quantity: int = 1) -> None:
        """
        Add a furniture item to the inventory. 
        If the item already exists, update its quantity.

        :param furniture: The furniture object to add.
        :param quantity: The number of units to add (default is 1).
        """
        if furniture in self.items:
            self.items[furniture] += quantity
        else:
            self.items[furniture] = quantity

    def remove_item(self, furniture: Furniture, quantity: int = 1) -> bool:
        """
        Remove a certain quantity of the item from the inventory. 
        If the quantity reaches zero, remove it completely.

        :param furniture: The furniture object to remove.
        :param quantity: The number of units to remove (default is 1).
        :return: True if removal succeeded, False if it failed (e.g., not enough in stock).
        """
        if furniture not in self.items:
            return False

        if self.items[furniture] < quantity:
            return False

        self.items[furniture] -= quantity
        if self.items[furniture] <= 0:
            del self.items[furniture]
        return True

    def update_quantity(self, furniture: Furniture, new_quantity: int) -> bool:
        """
        Update the quantity of a specific furniture item in the inventory.

        :param furniture: The furniture object to update.
        :param new_quantity: The new quantity.
        :return: True if the update was successful, False if the furniture isn't in the inventory.
        """
        if furniture not in self.items:
            return False

        self.items[furniture] = new_quantity
        if new_quantity <= 0:
            del self.items[furniture]
        return True

    # ----------------------------------------------------------------
    # Search Method
    # ----------------------------------------------------------------

    from typing import List, Optional, Type

    def search(
        self,
        name_substring: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        furniture_type: Optional[Type] = None
    ) -> List["Furniture"]:
        """
        Perform a flexible search across all furniture items in the inventory.

        This method can filter by:
        - Partial name match (case-insensitive).
        - Price range (min_price to max_price).
        - Furniture type (class).

        :param name_substring: Text to search for in the furniture name (case-insensitive).
        :param min_price: The minimum price. If None, no lower-bound price check is performed.
        :param max_price: The maximum price. If None, no upper-bound price check is performed.
        :param furniture_type: The class of the furniture (e.g., Chair, Table). If None,
                            no type check is performed.
        :return: A list of Furniture objects matching all specified criteria.
        """
        results = []

        for furniture_item in self.items.keys():
            # 1. Check name substring, if provided
            if name_substring is not None:
                if name_substring.lower() not in furniture_item.name.lower():
                    continue  # Doesn't match this filter, skip

            # 2. Check price range, if provided
            if (min_price is not None and furniture_item.price < min_price) or \
            (max_price is not None and furniture_item.price > max_price):
                continue  # Price out of range, skip

            # 3. Check furniture type, if provided
            if furniture_type is not None:
                if not isinstance(furniture_item, furniture_type):
                    continue  # Wrong type, skip

            # If all filters passed (or were not provided), add to results
            results.append(furniture_item)

        return results
    


### Pat 3 ###

import hashlib
from typing import Dict, List, Optional


class User:
    """
    A class that show both the 'User' data model and the user management system.

    This class includes:
      - Instance-level attributes and methods for a single user
        (name, email, password_hash, address, etc.).
      - Class-level data structures and methods for managing multiple
        users (register, login, retrieve, delete, etc.).

    Attributes (instance-level):
        name (str): The user's name.
        email (str): The user's unique email address (identifier).
        password_hash (str): The hashed password for authentication.
        address (str): The user's address (optional).
        order_history (List[str]): A list containing details about past orders.

    Attributes (class-level):
        _users (Dict[str, User]): A dictionary storing all user objects,
                                  keyed by email.
    """

    _users: Dict[str, "User"] = {}

    def __init__(
        self,
        name: str,
        email: str,
        password_hash: str,
        address: str = "",
        order_history: Optional[List[str]] = None
    ):
        """
        Initialize a User instance.

        :param name: The user's name.
        :param email: The user's unique email address.
        :param password_hash: The SHA-256 hash of the user's password.
        :param address: The user's address (optional).
        :param order_history: A list containing the user's order history (optional).
        """
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.address = address
        self.order_history = order_history if order_history is not None else []

    # ----------------------------------------------------------------
    # Class-Level Methods (User Management)
    # ----------------------------------------------------------------

    @classmethod
    def register_user(cls, name: str, email: str, raw_password: str, address: str = "") -> "User":
        """
        Register a new user with the provided details.

        :param name: The user's name.
        :param email: The user's unique email address.
        :param raw_password: The user's plain-text password (will be hashed).
        :param address: The user's address (optional).
        :return: The newly created User object.
        :raises ValueError: If a user with the same email already exists.
        """
        if email in cls._users:
            raise ValueError(f"A user with email '{email}' already exists.")

        password_hash = cls._hash_password(raw_password)
        user = cls(name, email, password_hash, address)
        cls._users[email] = user
        return user

    @classmethod
    def login_user(cls, email: str, raw_password: str) -> Optional["User"]:
        """
        Attempt to log in a user by verifying their email and password.

        :param email: The user's email.
        :param raw_password: The plain-text password provided by the user.
        :return: The User object if login is successful, or None otherwise.
        """
        user = cls._users.get(email)
        if user and user.check_password(raw_password):
            return user
        return None

    @classmethod
    def get_user(cls, email: str) -> Optional["User"]:
        """
        Retrieve a user by their email address.

        :param email: The email of the user to retrieve.
        :return: The User object if found, or None if no user with that email exists.
        """
        return cls._users.get(email)

    @classmethod
    def delete_user(cls, email: str) -> bool:
        """
        Remove a user from the system.

        :param email: The email of the user to remove.
        :return: True if the user was successfully removed, False otherwise.
        """
        if email in cls._users:
            del cls._users[email]
            return True
        return False

    # ----------------------------------------------------------------
    # Instance-Level Methods (Per-User Functionality)
    # ----------------------------------------------------------------

    def set_password(self, raw_password: str) -> None:
        """
        Set (or reset) the user's password by hashing it.

        :param raw_password: The plain-text password.
        """
        self.password_hash = self._hash_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """
        Verify that the provided plain-text password matches the stored hash.

        :param raw_password: The plain-text password to check.
        :return: True if the password is correct, False otherwise.
        """
        return self._hash_password(raw_password) == self.password_hash

    def update_profile(self, name: Optional[str] = None, address: Optional[str] = None) -> None:
        """
        Update the user's profile information (e.g., name and address).

        :param name: The new name of the user (if provided).
        :param address: The new address of the user (if provided).
        """
        if name is not None:
            self.name = name
        if address is not None:
            self.address = address

    def add_order(self, order_info: str) -> None:
        """
        Add an order entry to the user's order history.

        :param order_info: A string containing order details (e.g., item name, date).
        """
        self.order_history.append(order_info)

    @staticmethod
    def _hash_password(raw_password: str) -> str:
        """
        Hash a plain-text password using SHA-256.

        :param raw_password: The plain-text password to hash.
        :return: The SHA-256 hexadecimal digest of the password.
        """
        return hashlib.sha256(raw_password.encode('utf-8')).hexdigest()
    


### Part 4 ###


from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional


# --------------------------------------------------------------------
# Composite Pattern: CartComponent (Abstract Base Class)
# --------------------------------------------------------------------
class CartComponent(ABC):
    """
    The abstract base class for cart components (both leaves and composites).
    Each component must implement methods to get its price and apply discounts.
    """

    @abstractmethod
    def get_price(self) -> float:
        """Return the total price for this component."""
        pass

    @abstractmethod
    def apply_discount(self, percentage: float) -> None:
        """
        Apply a discount to this component (leaf or composite).
        :param percentage: A value 0-100 representing the discount percentage.
        """
        pass

    def add(self, component: CartComponent) -> None:
        """
        Optionally implemented by composite items to add child components.
        By default, leaves raise NotImplementedError.
        """
        raise NotImplementedError("This component cannot have children.")

    def remove(self, component: CartComponent) -> None:
        """
        Optionally implemented by composite items to remove child components.
        By default, leaves raise NotImplementedError.
        """
        raise NotImplementedError("This component does not support removing children.")


# --------------------------------------------------------------------
# Composite Pattern: LeafItem (e.g., Furniture, Accessory)
# --------------------------------------------------------------------
class LeafItem(CartComponent):
    """
    Represents a single item in the cart (e.g., a piece of furniture or an accessory).
    
    Attributes:
        name (str): Descriptive name of the item.
        unit_price (float): The unit price of the item.
        quantity (int): How many units of this item.
    """

    def __init__(self, name: str, unit_price: float, quantity: int = 1):
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


# --------------------------------------------------------------------
# Composite Pattern: CompositeItem (Optional Bundles or Collections)
# --------------------------------------------------------------------
class CompositeItem(CartComponent):
    """
    Represents a composite item that can contain multiple CartComponents
    (both LeafItem and other CompositeItem objects).
    """

    def __init__(self, name: str):
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


# --------------------------------------------------------------------
# ShoppingCart (Uses Composite Pattern for Different Item Types)
# --------------------------------------------------------------------
class ShoppingCart:
    """
    A ShoppingCart that allows users to add or remove items,
    view the total price, and apply discounts to individual items or the entire cart.
    """

    def __init__(self, name: str = "ShoppingCart"):
        # Root composite to store all cart components
        self.root = CompositeItem(name=name)

    def add_item(self, item: CartComponent) -> None:
        """
        Add a cart component (leaf or composite) to the shopping cart.
        :param item: A CartComponent object to add.
        """
        self.root.add(item)

    def remove_item(self, item: CartComponent) -> None:
        """
        Remove a specific component (leaf or composite) from the cart.
        :param item: The CartComponent to remove.
        """
        self.root.remove(item)

    def get_total_price(self) -> float:
        """
        Return the total price of all items in the cart.
        """
        return self.root.get_price()

    def apply_discount(self, percentage: float, target: Optional[CartComponent] = None) -> None:
        """
        Apply a discount to the entire cart or a specific component.
        
        :param percentage: A float 0-100 representing the discount percentage.
        :param target: If provided, apply discount only to this component; otherwise,
                       apply to the entire cart.
        """
        if target is not None:
            target.apply_discount(percentage)
        else:
            self.root.apply_discount(percentage)

    def view_cart(self) -> str:
        """
        Return a string listing the cart components and their prices.
        """
        if not self.root._children:
            return "Shopping cart is empty."

        lines = [f"Cart '{self.root.name}' contents:\n"]
        for component in self.root._children:
            lines.append(f"- Item: {component}, Price: {component.get_price():.2f}")
        lines.append(f"\nTotal price: {self.get_total_price():.2f}")
        return "\n".join(lines)



### Part 5 ###


from typing import Optional

from user_management import User  # From Part 3 (your User class)
from inventory import Inventory   # From Part 2
from shopping_cart import ShoppingCart, LeafItem, CompositeItem, CartComponent  # From Part 4


class Checkout:
    """
    A Checkout system that handles:
      - Collecting user info (address, payment method).
      - Validating the shopping cart against available inventory.
      - Processing payment (mock implementation).
      - Finalizing the order (updating inventory, user order history).
    """

    def __init__(self, user: User, cart: ShoppingCart, inventory: Inventory):
        """
        Initialize a Checkout process with a specific user, cart, and inventory.

        :param user: The user who is checking out.
        :param cart: The user's ShoppingCart (containing a Composite of items).
        :param inventory: The Inventory instance to validate and update.
        """
        self.user = user
        self.cart = cart
        self.inventory = inventory

        self.payment_method: Optional[str] = None
        self.address: Optional[str] = None
        self.order_finalized = False

    def set_payment_method(self, method: str) -> None:
        """
        Set the user's desired payment method (e.g., "Credit Card", "PayPal", etc.).

        :param method: The payment method as a string.
        """
        self.payment_method = method

    def set_address(self, address: str) -> None:
        """
        Set the shipping or billing address for the order.

        :param address: The address as a string.
        """
        self.address = address

    def validate_cart(self) -> bool:
        """
        Check that all items in the cart are in stock in the inventory.

        :return: True if the cart is valid (all items in stock), False otherwise.
        """
        # Retrieve a flat list of all LeafItems (since composites can contain leaves)
        leaf_items = self._collect_leaf_items(self.cart.root)

        for item in leaf_items:
            # For simplicity, assume 'item' is something like LeafItem(name="Chair", unit_price=..., quantity=...)
            # and that 'item.name' corresponds to a Furniture.name in the Inventory.
            # You might adapt this if you store references to the actual Furniture objects.
            
            # We look up inventory by searching for a furniture that matches 'item.name'.
            furniture_in_inventory = self._find_furniture_by_name(item.name)
            if not furniture_in_inventory:
                return False  # Item not found in inventory at all

            required_qty = item.quantity
            available_qty = self.inventory.get_quantity(furniture_in_inventory)
            if required_qty > available_qty:
                return False  # Not enough in stock

        return True

    def process_payment(self) -> bool:
        """
        Mock the payment processing. In a real system, we'd integrate
        with a payment gateway. Here, we simply return True to indicate success.

        :return: True if payment succeeded, False otherwise.
        """
        if not self.payment_method:
            return False  # No payment method selected
        # Mocking payment success:
        return True

    def finalize_order(self) -> bool:
        """
        Finalize the order by updating inventory, adding to user history,
        and marking the order as finalized.

        :return: True if order was finalized successfully, False otherwise.
        """
        if self.order_finalized:
            return False  # Already finalized
        if not self.validate_cart():
            return False  # Can't finalize if validation fails
        if not self.process_payment():
            return False  # Payment failed

        # Deduct the items from inventory
        leaf_items = self._collect_leaf_items(self.cart.root)
        for item in leaf_items:
            furniture_in_inventory = self._find_furniture_by_name(item.name)
            if furniture_in_inventory:
                self.inventory.remove_item(furniture_in_inventory, item.quantity)

        # Record an "order" in the user's history
        # For simplicity, just store a string with order details.
        order_summary = (
            f"Order for {self.user.name}, "
            f"Items: {[f'{i.name} x {i.quantity}' for i in leaf_items]}, "
            f"Ship to: {self.address}, "
            f"Payment via: {self.payment_method}, "
            f"Total: {self.cart.get_total_price():.2f}"
        )
        self.user.add_order(order_summary)

        self.order_finalized = True
        return True

    # ----------------------------------------------------------------
    # Helper Methods
    # ----------------------------------------------------------------

    def _collect_leaf_items(self, component: CartComponent) -> list[LeafItem]:
        """
        Recursively collect all LeafItems from a CartComponent tree.
        """
        # If it's a leaf, just return it in a list
        if isinstance(component, LeafItem):
            return [component]

        # If it's a composite, gather from children
        if isinstance(component, CompositeItem):
            result = []
            for child in component._children:
                result.extend(self._collect_leaf_items(child))
            return result

        return []

    def _find_furniture_by_name(self, name: str):
        """
        A simple helper to locate a Furniture object in the inventory
        by matching the 'name' attribute. Returns None if not found.
        """
        for furniture_item in self.inventory.items.keys():
            if furniture_item.name == name:
                return furniture_item
        return None

