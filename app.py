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











### PART 2







from typing import Dict, List
from furniture import Furniture, Chair, Table, Sofa, Lamp, Shelf

class Inventory:
    """
    מחלקה לניהול מלאי הרהיטים. ממומשת כ-Singleton כדי להבטיח מופע יחיד של המלאי.
    """

    _instance = None  # משתנה סטטי שיחזיק את המופע היחיד של המחלקה

    def __init__(self):
        """
        מאתחל את מבנה הנתונים של המלאי:
        - items: מילון שממפה אובייקט רהיט (furniture) למספר הכמות הקיימת במלאי.
        """
        if Inventory._instance is not None:
            # מניעת יצירת מופע נוסף של Singleton
            raise Exception("Inventory is a singleton class. Use Inventory.get_instance() instead.")
        self.items: Dict[Furniture, int] = {}
        Inventory._instance = self

    @staticmethod
    def get_instance():
        """
        מחזיר את המופע הקיים של המחלקה, או יוצר אחד חדש אם לא קיים.
        """
        if Inventory._instance is None:
            Inventory()
        return Inventory._instance

    # ----------------------------------------------------------------
    # CRUD Operations (Create/Read/Update/Delete)
    # ----------------------------------------------------------------

    def add_item(self, furniture: Furniture, quantity: int = 1) -> None:
        """
        מוסיף פריט למלאי, אם כבר קיים - מעדכן את הכמות.
        :param furniture: אובייקט רהיט להוספה
        :param quantity: כמות להוספה
        """
        if furniture in self.items:
            self.items[furniture] += quantity
        else:
            self.items[furniture] = quantity

    def remove_item(self, furniture: Furniture, quantity: int = 1) -> bool:
        """
        מסיר כמות מסוימת של הפריט מהמלאי. אם הכמות מגיעה לאפס - מסיר לחלוטין.
        :param furniture: הרהיט להסרה
        :param quantity: כמה להסיר
        :return: True אם הצלחנו להסיר, False אם לא היה ניתן להסיר (למשל אם אין מספיק במלאי).
        """
        if furniture not in self.items:
            return False

        if self.items[furniture] < quantity:
            return False

        self.items[furniture] -= quantity
        if self.items[furniture] <= 0:
            del self.items[furniture]  # מסירים לגמרי מהמילון
        return True

    def update_quantity(self, furniture: Furniture, new_quantity: int) -> bool:
        """
        מעדכן את הכמות של פריט מסוים במלאי.
        :param furniture: הרהיט לעדכן
        :param new_quantity: הכמות החדשה
        :return: True אם בוצע בהצלחה, False אם הרהיט לא קיים במלאי.
        """
        if furniture not in self.items:
            return False
        self.items[furniture] = new_quantity
        if new_quantity <= 0:
            del self.items[furniture]
        return True

    # ----------------------------------------------------------------
    # Search Methods
    # ----------------------------------------------------------------

    def search_by_name(self, name_substring: str) -> List[Furniture]:
        """
        מחזיר רשימת רהיטים שהשם שלהם מכיל את הטקסט המבוקש (case-insensitive).
        :param name_substring: טקסט לחיפוש בשם הרהיט
        :return: רשימת אובייקטי רהיט תואמים.
        """
        name_substring = name_substring.lower()
        results = []
        for f in self.items.keys():
            if name_substring in f.name.lower():
                results.append(f)
        return results

    def search_by_price_range(self, min_price: float, max_price: float) -> List[Furniture]:
        """
        מחזיר רשימת רהיטים שהמחיר שלהם נמצא בטווח המבוקש [min_price, max_price].
        :param min_price: מחיר מינימלי
        :param max_price: מחיר מקסימלי
        :return: רשימת אובייקטי רהיט העומדים בתנאי
        """
        results = []
        for f in self.items.keys():
            if min_price <= f.price <= max_price:
                results.append(f)
        return results

    def search_by_type(self, furniture_type: type) -> List[Furniture]:
        """
        מחזיר רשימת רהיטים מהסוג המבוקש (Chair, Table, Sofa וכו').
        :param furniture_type: מחלקת הרהיט (Chair, Table וכו').
        :return: רשימת רהיטים המתאימים לסוג
        """
        results = []
        for f in self.items.keys():
            if isinstance(f, furniture_type):
                results.append(f)
        return results

    # ----------------------------------------------------------------
    # Utilities
    # ----------------------------------------------------------------

    def get_quantity(self, furniture: Furniture) -> int:
        """
        מחזיר כמה יחידות של רהיט מסוים יש במלאי, או 0 אם לא קיים.
        """
        return self.items.get(furniture, 0)

    def total_unique_items(self) -> int:
        """
        מחזיר את מספר סוגי הרהיטים במלאי.
        """
        return len(self.items)

    def __str__(self) -> str:
        """
        מציג תוכן מלאי בצורה קריאה.
        """
        if not self.items:
            return "Inventory is empty."
        lines = ["Inventory:"]
        for furniture, qty in self.items.items():
            lines.append(f"{furniture} | Quantity: {qty}")
        return "\n".join(lines)
