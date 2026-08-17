"""
cli.py

A simple command-line interface for the Inventory Management API.
This talks to app.py over HTTP, exactly like a real client would
(Postman, a website, a mobile app, etc).

Run app.py FIRST (in another terminal), then run this file.
"""

import requests

API_URL = "http://127.0.0.1:5000"


def view_all_items():
    response = requests.get(f"{API_URL}/items")
    items = response.json()

    if not items:
        print("\nNo items in inventory.\n")
        return

    print("\n--- INVENTORY ---")
    for item in items:
        print(f"  [{item['id']}] {item['product_name']} "
              f"({item['brands']}) - qty: {item['quantity']} "
              f"- ${item['price']}")
    print()


def view_item_by_id():
    item_id = input("Enter item ID: ").strip()
    response = requests.get(f"{API_URL}/items/{item_id}")

    if response.status_code == 404:
        print(f"\n{response.json()['error']}\n")
        return

    item = response.json()
    print("\n--- ITEM DETAILS ---")
    for key, value in item.items():
        print(f"  {key}: {value}")
    print()


def add_item_manually():
    print("\nEnter new item details:")
    product_name = input("  Product name: ").strip()
    brands = input("  Brand: ").strip()
    barcode = input("  Barcode: ").strip()
    quantity = input("  Quantity: ").strip()
    price = input("  Price: ").strip()

    payload = {
        "product_name": product_name,
        "brands": brands,
        "barcode": barcode,
        "quantity": int(quantity) if quantity.isdigit() else 0,
        "price": float(price) if price else 0.0,
    }

    response = requests.post(f"{API_URL}/items", json=payload)

    if response.status_code == 201:
        print(f"\nCreated item with id {response.json()['id']}\n")
    else:
        print(f"\nError: {response.json()}\n")


def add_item_by_barcode():
    barcode = input("Enter barcode to look up on OpenFoodFacts: ").strip()
    response = requests.get(f"{API_URL}/items/fetch/{barcode}")

    if response.status_code == 201:
        item = response.json()
        print(f"\nAdded '{item['product_name']}' with id {item['id']}\n")
    else:
        print(f"\n{response.json().get('error', 'Something went wrong')}\n")


def edit_item():
    item_id = input("Enter item ID to edit: ").strip()

    print("Leave a field blank to keep it unchanged.")
    product_name = input("  New product name: ").strip()
    quantity = input("  New quantity: ").strip()
    price = input("  New price: ").strip()

    payload = {}
    if product_name:
        payload["product_name"] = product_name
    if quantity:
        payload["quantity"] = int(quantity)
    if price:
        payload["price"] = float(price)

    response = requests.patch(f"{API_URL}/items/{item_id}", json=payload)

    if response.status_code == 200:
        print("\nItem updated.\n")
    else:
        print(f"\nError: {response.json()}\n")


def delete_item():
    item_id = input("Enter item ID to delete: ").strip()
    response = requests.delete(f"{API_URL}/items/{item_id}")

    if response.status_code == 200:
        print(f"\n{response.json()['message']}\n")
    else:
        print(f"\nError: {response.json()}\n")


MENU = """
==== INVENTORY MANAGEMENT CLI ====
1. View all items
2. View item by ID
3. Add item manually
4. Add item by barcode (OpenFoodFacts)
5. Edit item
6. Delete item
7. Exit
"""


def main():
    actions = {
        "1": view_all_items,
        "2": view_item_by_id,
        "3": add_item_manually,
        "4": add_item_by_barcode,
        "5": edit_item,
        "6": delete_item,
    }

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "7":
            print("Goodbye!")
            break

        action = actions.get(choice)
        if action is None:
            print("\nInvalid choice, try again.\n")
            continue

        try:
            action()
        except requests.exceptions.ConnectionError:
            print("\nCouldn't reach the API. Is app.py running? "
                  "(python app.py)\n")


if __name__ == "__main__":
    main()
