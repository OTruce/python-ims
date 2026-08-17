"""
database.py

This is our MOCK database. In a real production app this would be
a real database (Postgres, SQLite, MongoDB, etc). For this lab, we
keep it simple: a plain Python list of dictionaries, living in memory.

Each item is shaped roughly like data from the OpenFoodFacts API,
per the lab instructions, plus fields we need for inventory
management (id, quantity, price).
"""

# This list IS our database. Every function in app.py will
# read from / write to this list.
inventory_db = [
    {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "barcode": "0025293001164",
        "ingredients_text": "Filtered water, almonds, cane sugar",
        "quantity": 25,
        "price": 3.99,
    },
    {
        "id": 2,
        "product_name": "Peanut Butter",
        "brands": "Jif",
        "barcode": "0051500255162",
        "ingredients_text": "Roasted peanuts, sugar, molasses, salt",
        "quantity": 40,
        "price": 4.49,
    },
    {
        "id": 3,
        "product_name": "Whole Wheat Bread",
        "brands": "Dave's Killer Bread",
        "barcode": "0793573330217",
        "ingredients_text": "Whole wheat flour, water, honey, yeast",
        "quantity": 15,
        "price": 5.29,
    },
]


def get_next_id():
    """
    Figures out the next available ID by looking at the highest
    existing ID and adding 1. If the DB is empty, start at 1.
    """
    if not inventory_db:
        return 1
    return max(item["id"] for item in inventory_db) + 1


def find_item_by_id(item_id):
    """
    Loops through the mock DB and returns the item with a matching id,
    or None if nothing matches. This is our "SELECT * WHERE id = ?"
    """
    for item in inventory_db:
        if item["id"] == item_id:
            return item
    return None
