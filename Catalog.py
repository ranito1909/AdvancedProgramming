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