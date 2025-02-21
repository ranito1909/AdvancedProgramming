from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Optional
import hashlib
from enum import Enum
from datetime import datetime


### Part 1 ### 


# --------------------------------------------------------------------
# Furniture (Abstract Base Class)
# --------------------------------------------------------------------
class Furniture(ABC):
    """
    An abstract base class that represents a general piece of furniture.
    This class enforces certain methods (apply_discount, apply_tax, check_availability)
    that concrete furniture classes must implement.
    """

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        dimensions: Tuple[float, ...],
    ) -> None:
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

    @abstractmethod
    def apply_tax(self, tax_rate: float) -> None:
        """
        Apply a tax (e.g., VAT) to the price.
        For instance, a tax_rate of 0.17 represents 17% tax.
        """

    @abstractmethod
    def check_availability(self) -> bool:
        """
        Check if this piece of furniture is in stock.
        In the child classes, we actually look at the Inventory to see availability.
        """

    def __str__(self) -> str:
        """
        Provide a string representation of the furniture item, typically
        showing its name, description, and price.
        """
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
        cushion_material: str,
    ) -> None:
        """
        Initialize the Chair with its additional cushion material property.

        :param name: The name of the furniture (chair).
        :param description: A short description.
        :param price: The base price.
        :param dimensions: Dimensions tuple (e.g., width, depth, height).
        :param cushion_material: The material used for the chair's cushion.
        """
        super().__init__(name, description, price, dimensions)
        self.cushion_material = cushion_material

    def apply_discount(self, percentage: float) -> None:
        """
        Subtract a specified percentage from the chair's current price.
        """
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        """
        Add tax to the current chair price using the provided tax_rate.
        Example: tax_rate=0.17 => 17% tax.
        """
        self.price *= 1 + tax_rate

    def check_availability(self) -> bool:
        """
        Check if this piece of furniture is in stock in the Inventory.
        We retrieve the singleton Inventory and see if quantity > 0.
        """
        inventory = Inventory.get_instance()
        return inventory.items.get(self, 0) > 0

    def __str__(self) -> str:
        """
        Extend the base string representation with cushion material details.
        """
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
        frame_material: str,
    ) -> None:
        """
        Initialize the Table with its frame material.

        :param name: The table's name.
        :param description: Short description.
        :param price: The base price of the table.
        :param dimensions: Dimensions (width, depth, height, etc.).
        :param frame_material: Type of frame material.
        """
        super().__init__(name, description, price, dimensions)
        self.frame_material = frame_material

    def apply_discount(self, percentage: float) -> None:
        """
        Reduce the table price by the specified percentage discount.
        """
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        """
        Increase the table price by multiplying with (1 + tax_rate).
        """
        self.price *= 1 + tax_rate

    def check_availability(self) -> bool:
        """
        Check if this table is in stock in the Inventory.
        """
        inventory = Inventory.get_instance()
        return inventory.items.get(self, 0) > 0

    def __str__(self) -> str:
        """
        Extend the base string representation with frame material details.
        """
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
        capacity: int,
    ) -> None:
        """
        Initialize the Sofa with a capacity.

        :param name: Name of the sofa.
        :param description: Short description.
        :param price: Base price.
        :param dimensions: Dimensions.
        :param capacity: How many people can sit on this sofa.
        """
        super().__init__(name, description, price, dimensions)
        self.capacity = capacity

    def apply_discount(self, percentage: float) -> None:
        """
        Reduce the sofa price by the given discount percentage.
        """
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        """
        Increase the sofa price by applying the given tax rate.
        """
        self.price *= 1 + tax_rate

    def check_availability(self) -> bool:
        """
        Check if this sofa is in stock in the Inventory.
        """
        inventory = Inventory.get_instance()
        return inventory.items.get(self, 0) > 0

    def __str__(self) -> str:
        """
        Extend the base string with capacity details.
        """
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
        light_source: str,
    ) -> None:
        """
        Initialize the Lamp with a light_source attribute.

        :param name: Lamp name.
        :param description: Short description.
        :param price: Base price.
        :param dimensions: Dimensions.
        :param light_source: Type of light (e.g., LED, fluorescent).
        """
        super().__init__(name, description, price, dimensions)
        self.light_source = light_source

    def apply_discount(self, percentage: float) -> None:
        """
        Reduce the lamp price by the given percentage.
        """
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        """
        Increase the lamp price by multiplying with (1 + tax_rate).
        """
        self.price *= 1 + tax_rate

    def check_availability(self) -> bool:
        """
        Check if this lamp is in stock in the Inventory.
        """
        inventory = Inventory.get_instance()
        return inventory.items.get(self, 0) > 0

    def __str__(self) -> str:
        """
        Extend the base string with light source info.
        """
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
        wall_mounted: bool,
    ) -> None:
        """
        Initialize the Shelf with wall_mounted property.

        :param name: Shelf name.
        :param description: Short description.
        :param price: Base price.
        :param dimensions: Dimensions.
        :param wall_mounted: True if shelf mounts to a wall.
        """
        super().__init__(name, description, price, dimensions)
        self.wall_mounted = wall_mounted

    def apply_discount(self, percentage: float) -> None:
        """
        Reduce the shelf price by the discount percentage.
        """
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        """
        Increase the shelf price based on the tax rate.
        """
        self.price *= 1 + tax_rate

    def check_availability(self) -> bool:
        """
        Check if this shelf is in stock in the Inventory.
        """
        inventory = Inventory.get_instance()
        return inventory.items.get(self, 0) > 0

    def __str__(self) -> str:
        """
        Extend the base string with wall-mounted info.
        """
        base_str = super().__str__()
        return f"{base_str}, Wall Mounted: {self.wall_mounted}"


### PART 2 ###


class Inventory:
    """
    A Singleton class that manages an inventory of furniture.
    Only one instance of this class can exist.
    """

    _instance = None  # Static variable to hold the single instance of the class

    def __init__(self) -> None:
        """
        Initialize the data structure for the inventory:
        - items: a dictionary mapping a Furniture object to the quantity in stock.
        """
        if Inventory._instance is not None:
            raise Exception(
                "Inventory is a singleton class. Use Inventory.get_instance() instead."
            )
        self.items: Dict[Furniture, int] = {}
        Inventory._instance = self

    @staticmethod
    def get_instance() -> "Inventory":
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
        :return: True if removal succeeded, False if it failed
                 (e.g., not enough in stock).
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
        :return: True if the update was successful,
                 False if the furniture isn't in the inventory.
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
    from typing import List as _List, Optional as _Optional, Type as _Type

    def search(
        self,
        name_substring: _Optional[str] = None,
        min_price: _Optional[float] = None,
        max_price: _Optional[float] = None,
        furniture_type: _Optional[_Type] = None,
    ) -> _List["Furniture"]:
        """
        Perform a flexible search across all furniture items in the inventory.

        This method can filter by:
        - Partial name match (case-insensitive).
        - Price range (min_price to max_price).
        - Furniture type (class).

        :param name_substring: Text to search for in the furniture name (case-insensitive).
        :param min_price: The minimum price. If None, no lower-bound check is performed.
        :param max_price: The maximum price. If None, no upper-bound check is performed.
        :param furniture_type: The class of the furniture (Chair, Table, etc.).
        :return: A list of Furniture objects matching all specified criteria.
        """
        results = []

        for furniture_item in self.items.keys():
            # 1. Check name substring
            if name_substring is not None:
                if name_substring.lower() not in furniture_item.name.lower():
                    continue

            # 2. Check price range
            if min_price is not None and furniture_item.price < min_price:
                continue
            if max_price is not None and furniture_item.price > max_price:
                continue

            # 3. Check furniture type
            if furniture_type is not None:
                if not isinstance(furniture_item, furniture_type):
                    continue

            # Passed all filters
            results.append(furniture_item)

        return results


### Pat 3 ###


class User:
    """
    A class that shows both the 'User' data model and the user management system.

    This class includes:
      - Instance-level attributes and methods for a single user
        (name, email, password_hash, address, etc.).
      - Class-level data structures and methods for managing multiple
        users (register, login, retrieve, delete, etc.).
    """

    _users: Dict[str, "User"] = {}

    def __init__(
        self,
        name: str,
        email: str,
        password_hash: str,
        address: str = "",
        order_history: Optional[List[str]] = None,
    ) -> None:
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
    def register_user(
        cls, name: str, email: str, raw_password: str, address: str = ""
    ) -> "User":
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

    def update_profile(
        self, name: Optional[str] = None, address: Optional[str] = None
    ) -> None:
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
        return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


### Part 4 ###


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
        """
        Return the total price for this component.
        """

    @abstractmethod
    def apply_discount(self, percentage: float) -> None:
        """
        Apply a discount to this component (leaf or composite).
        :param percentage: A value 0-100 representing the discount percentage.
        """

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

    def __init__(self, name: str, unit_price: float, quantity: int = 1) -> None:
        """
        Initialize a leaf item with name, unit price, and quantity.

        :param name: The name/identifier of the item (e.g., "Chair").
        :param unit_price: The base price of one unit of this item.
        :param quantity: How many units are being purchased.
        """
        self.name = name
        self.unit_price = unit_price
        self.quantity = quantity
        self._current_price = unit_price  # Tracks price after discount

    def get_price(self) -> float:
        """
        Calculate the total price based on current (possibly discounted) price * quantity.
        """
        return self._current_price * self.quantity

    def apply_discount(self, percentage: float) -> None:
        """
        Reduce the item price by the specified discount percentage (0-100).
        This only affects future calculations since it modifies _current_price.
        """
        if not (0 <= percentage <= 100):
            raise ValueError("Discount percentage must be between 0 and 100.")
        discount_amount = self.unit_price * (percentage / 100)
        self._current_price = self.unit_price - discount_amount

    def __str__(self) -> str:
        """
        String representation to easily see name, price, and quantity.
        """
        return (
            f"LeafItem({self.name}, Price={self.unit_price:.2f}, Qty={self.quantity})"
        )


# --------------------------------------------------------------------
# Composite Pattern: CompositeItem (Optional Bundles or Collections)
# --------------------------------------------------------------------
class CompositeItem(CartComponent):
    """
    Represents a composite item that can contain multiple CartComponents
    (both LeafItem and other CompositeItem objects).
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the composite with a name and an internal list of children.

        :param name: A label or identifier for this group of items (e.g., "Bundle A").
        """
        self.name = name
        self._children: List[CartComponent] = []

    def add(self, component: CartComponent) -> None:
        """
        Add a CartComponent (leaf or composite) as a child.
        """
        self._children.append(component)

    def remove(self, component: CartComponent) -> None:
        """
        Remove a child component from the composite.
        """
        self._children.remove(component)

    def get_price(self) -> float:
        """
        Sum up the prices of all child components.
        """
        return sum(child.get_price() for child in self._children)

    def apply_discount(self, percentage: float) -> None:
        """
        Apply a discount to every child component in this composite.
        """
        for child in self._children:
            child.apply_discount(percentage)

    def __str__(self) -> str:
        """
        Indicate this is a composite item, plus how many child components it has.
        """
        return f"CompositeItem({self.name}, children={len(self._children)})"


# --------------------------------------------------------------------
# ShoppingCart (Uses Composite Pattern for Different Item Types)
# --------------------------------------------------------------------
class ShoppingCart:
    """
    A ShoppingCart that allows users to add or remove items,
    view the total price, and apply discounts to individual items or the entire cart.
    """

    def __init__(self, name: str = "ShoppingCart") -> None:
        """
        Initialize the ShoppingCart with a root CompositeItem.
        :param name: The name/title of the cart (optional).
        """
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

    def apply_discount(
        self, percentage: float, target: Optional[CartComponent] = None
    ) -> None:
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


class Checkout:
    """
    A Checkout system that handles:
      - Collecting user info (address, payment method).
      - Validating the shopping cart against available inventory.
      - Processing payment (mock implementation).
      - Finalizing the order (updating inventory, user order history).
    """

    def __init__(self, user: User, cart: ShoppingCart, inventory: Inventory) -> None:
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
        leaf_items = self._collect_leaf_items(self.cart.root)

        for item in leaf_items:
            # We look up inventory by searching for a furniture that matches 'item.name'.
            furniture_in_inventory = self._find_furniture_by_name(item.name)
            if not furniture_in_inventory:
                return False

            required_qty = item.quantity
            available_qty = self.inventory.get_quantity(furniture_in_inventory)
            if required_qty > available_qty:
                return False

        return True

    def process_payment(self) -> bool:
        """
        Mock the payment processing. In a real system, we'd integrate
        with a payment gateway. Here, we simply return True to indicate success.

        :return: True if payment succeeded, False otherwise.
        """
        if not self.payment_method:
            return False
        return True

    def finalize_order(self) -> bool:
        """
        Finalize the order by updating inventory, adding to user history,
        and marking the order as finalized.

        :return: True if order was finalized successfully, False otherwise.
        """
        if self.order_finalized:
            return False
        if not self.validate_cart():
            return False
        if not self.process_payment():
            return False

        leaf_items = self._collect_leaf_items(self.cart.root)
        for item in leaf_items:
            furniture_in_inventory = self._find_furniture_by_name(item.name)
            if furniture_in_inventory:
                self.inventory.remove_item(furniture_in_inventory, item.quantity)

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
    def _collect_leaf_items(self, component: CartComponent) -> List[LeafItem]:
        """
        Recursively collect all LeafItems from a CartComponent tree.
        """
        if isinstance(component, LeafItem):
            return [component]

        if isinstance(component, CompositeItem):
            result = []
            for child in component._children:
                result.extend(self._collect_leaf_items(child))
            return result

        return []

    def _find_furniture_by_name(self, name: str) -> Optional[Furniture]:
        """
        A simple helper to locate a Furniture object in the inventory
        by matching the 'name' attribute. Returns None if not found.
        """
        for furniture_item in self.inventory.items.keys():
            if furniture_item.name == name:
                return furniture_item
        return None


### Part 6 ###


class OrderStatus(Enum):
    """
    Enum for various statuses an order can have.
    Possible values: PENDING, SHIPPED, DELIVERED, CANCELED.
    """

    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class Order:
    """
    Represents a single purchase/order made by a user.

    Attributes:
        user: The user who placed the order.
        items: A list of items purchased (e.g., LeafItem objects).
        total_price: The total cost of all items at checkout time.
        status: Current status of the order (pending, shipped, etc.).
        created_at: A timestamp indicating when the order was created.
    """

    def __init__(
        self,
        user: User,
        items: List[LeafItem],
        total_price: float,
        status: OrderStatus = OrderStatus.PENDING,
    ) -> None:
        """
        Initialize an Order object.

        :param user: The user who placed the order.
        :param items: A list of LeafItem objects representing purchased goods.
        :param total_price: The total cost for the order at checkout time.
        :param status: The current status of the order, defaults to PENDING.
        """
        self.user = user
        self.items = items
        self.total_price = total_price
        self.status = status
        self.created_at = datetime.now()

    def set_status(self, new_status: OrderStatus) -> None:
        """
        Update the status of the order (e.g., from pending to shipped).
        """
        self.status = new_status

    def get_status(self) -> OrderStatus:
        """
        Return the current status of the order.
        """
        return self.status

    def __str__(self) -> str:
        """
        Provide a string representation of the order details.
        """
        item_descriptions = ", ".join(f"{i.name} x {i.quantity}" for i in self.items)
        return (
            f"Order for {self.user.name} | Status: {self.status.value}\n"
            f"Items: {item_descriptions}\n"
            f"Total Price: {self.total_price:.2f}\n"
            f"Created at: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
