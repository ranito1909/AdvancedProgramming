from abc import ABC, abstractmethod
from typing import Tuple

# --------------------------------------------------------------------
# Furniture (Abstract Base Class)
# --------------------------------------------------------------------
class Furniture(ABC):
    """
    מחלקה אבסטרקטית (Abstract Base Class) המייצגת רהיט כללי.
    """

    def __init__(self, name: str, description: str, price: float, dimensions: Tuple[float, ...]):
        """
        :param name: שם הרהיט
        :param description: תיאור קצר של הרהיט
        :param price: מחיר בסיסי של הרהיט לפני הנחות/מע"מ
        :param dimensions: מימדי הרהיט כטאפל (רוחב, עומק, גובה וכד')
        """
        self.name = name
        self.description = description
        self.price = price
        self.dimensions = dimensions  # לדוגמה: (width, depth, height)

    @abstractmethod
    def apply_discount(self, percentage: float) -> None:
        """
        מפעילה הנחה על המחיר. אחוז ההנחה (percentage) הוא מספר בין 0 ל-100.
        """
        pass

    @abstractmethod
    def apply_tax(self, tax_rate: float) -> None:
        """
        מפעילה מע"מ (או מס אחר) על המחיר, למשל 0.17 עבור 17% מע"מ.
        """
        pass

    @abstractmethod
    def check_availability(self) -> bool:
        """
        בודקת אם יש רהיט זה במלאי. בשלב הזה פשוט נחזיר True או False.
        """
        pass

    def __str__(self) -> str:
        return f"{self.name} ({self.description}): {self.price:.2f} ₪"

# --------------------------------------------------------------------
# Chair (מחלקת כיסא)
# --------------------------------------------------------------------

class Chair(Furniture):
    
    "Cushion Material (str) - מחזיק מחרוזת המציינת את סוג הריפוד של הכסא"

    def __init__(self, name: str, description: str, price: float,
                 dimensions: Tuple[float, ...], cushion_material: str):
        super().__init__(name, description, price, dimensions)
        self.cushion_material = cushion_material
        

    def apply_discount(self, percentage: float) -> None:
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= (1 + tax_rate)

    def check_availability(self) -> bool:
        # באופן זמני נחזיר True. נרחיב בעתיד עם Inventory.
        return True

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Cushion Material: {self.cushion_material}"

# --------------------------------------------------------------------
# Table (מחלקת שולחן)
# --------------------------------------------------------------------
class Table(Furniture):
    
    "Frame Material (str) - מחזיק מחרוזת המציינת את סוג המסגרת של השולחן"

    def __init__(self, name: str, description: str, price: float,
                 dimensions: Tuple[float, ...], frame_material: str):
        super().__init__(name, description, price, dimensions)
        self.frame_material = frame_material

    def apply_discount(self, percentage: float) -> None:
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= (1 + tax_rate)

    def check_availability(self) -> bool:
        return True

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Frame Material: {self.frame_material}"

# --------------------------------------------------------------------
# Sofa (מחלקת ספה)
# --------------------------------------------------------------------
class Sofa(Furniture):
    
    "Capacity (int) -  מספר שלם המסמן את כמות האנשים שיכולים לשבת בספה"

    def __init__(self, name: str, description: str, price: float,
                 dimensions: Tuple[float, ...], capacity: int):
        super().__init__(name, description, price, dimensions)
        self.capacity = capacity

    def apply_discount(self, percentage: float) -> None:
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= (1 + tax_rate)

    def check_availability(self) -> bool:
        return True

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Capacity: {self.capacity}"

# --------------------------------------------------------------------
# Lamp (מחלקת מנורה)
# --------------------------------------------------------------------
class Lamp(Furniture):
    
    "Light Source (str) - מחזיק מחרוזת המציינת את סוג האור שנפלט מהמנורה"

    def __init__(self, name: str, description: str, price: float,
                 dimensions: Tuple[float, ...], light_source: str):        
        super().__init__(name, description, price, dimensions)
        self.light_source = light_source

    def apply_discount(self, percentage: float) -> None:
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= (1 + tax_rate)

    def check_availability(self) -> bool:
        return True

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Light Source: {self.light_source}"

# --------------------------------------------------------------------
# Shelf (מחלקת מדף)
# --------------------------------------------------------------------
class Shelf(Furniture):

    "Wall Mounted (bool) - משתנה בוליאני שמעיד על המדף האם הוא מתחבר לקיר"

    def __init__(self, name: str, description: str, price: float,
                 dimensions: Tuple[float, ...], wall_mounted: bool):
        super().__init__(name, description, price, dimensions)
        self.wall_mounted = wall_mounted
       

    def apply_discount(self, percentage: float) -> None:
        discount_amount = self.price * (percentage / 100)
        self.price -= discount_amount

    def apply_tax(self, tax_rate: float) -> None:
        self.price *= (1 + tax_rate)

    def check_availability(self) -> bool:
        return True

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str}, Wall Mounted: {self.wall_mounted}"