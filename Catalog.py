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