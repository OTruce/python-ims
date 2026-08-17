"""
app.py

The Flask REST API for our Inventory Management System.

Routes:
  GET    /items                -> list every item
  GET    /items/<id>           -> get one item
  POST   /items                -> create a new item
  PATCH  /items/<id>           -> update an existing item
  DELETE /items/<id>           -> delete an item
  GET    /items/fetch/<barcode>-> fetch product from OpenFoodFacts
                                   and add it to our inventory
"""

from flask import Flask, jsonify, request

from database import inventory_db, get_next_id, find_item_by_id
import external_api

app = Flask(__name__)


# ---------- READ ----------

@app.route("/items", methods=["GET"])
def get_items():
    """Return every item currently in inventory."""
    return jsonify(inventory_db), 200


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Return a single item by its id, or a 404 if it doesn't exist."""
    item = find_item_by_id(item_id)
    if item is None:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify(item), 200


# ---------- CREATE ----------

@app.route("/items", methods=["POST"])
def create_item():
    """
    Create a new inventory item manually.
    Expects a JSON body, e.g.:
    {
        "product_name": "Orange Juice",
        "brands": "Tropicana",
        "barcode": "0048500001234",
        "ingredients_text": "Orange juice",
        "quantity": 10,
        "price": 4.99
    }
    """
    data = request.get_json(silent=True)
    if not data or "product_name" not in data:
        return jsonify({"error": "product_name is required"}), 400

    new_item = {
        "id": get_next_id(),
        "product_name": data.get("product_name"),
        "brands": data.get("brands", "Unknown brand"),
        "barcode": data.get("barcode", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "quantity": data.get("quantity", 0),
        "price": data.get("price", 0.0),
    }
    inventory_db.append(new_item)
    return jsonify(new_item), 201


# ---------- UPDATE ----------

@app.route("/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item_by_id(item_id)
    if item is None:
        return jsonify({"error": f"Item {item_id} not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Only update fields the caller actually sent
    for field in ("product_name", "brands", "barcode",
                  "ingredients_text", "quantity", "price"):
        if field in data:
            item[field] = data[field]

    return jsonify(item), 200


# ---------- DELETE ----------

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item_by_id(item_id)
    if item is None:
        return jsonify({"error": f"Item {item_id} not found"}), 404

    inventory_db.remove(item)
    return jsonify({"message": f"Item {item_id} deleted"}), 200


# ---------- EXTERNAL API ----------

@app.route("/items/fetch/<barcode>", methods=["GET"])
def fetch_item_from_external(barcode):
    """
    Look up a barcode on OpenFoodFacts.
    """
    product = external_api.fetch_product_by_barcode(barcode)

    if product is None:
        return jsonify({"error": f"No product found for barcode {barcode}"}), 404

    product["id"] = get_next_id()
    inventory_db.append(product)
    return jsonify(product), 201


@app.route("/items/search", methods=["GET"])
def search_items_by_name():
    
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Query parameter 'name' is required"}), 400

    results = external_api.fetch_product_by_name(name)

    if not results:
        return jsonify({"error": f"No products found for '{name}'"}), 404

    return jsonify(results), 200


@app.route("/items/<int:item_id>/enhance", methods=["PATCH"])
def enhance_item(item_id):
    
    item = find_item_by_id(item_id)
    if item is None:
        return jsonify({"error": f"Item {item_id} not found"}), 404

    barcode = item.get("barcode")
    if not barcode:
        return jsonify({"error": "This item has no barcode to look up"}), 400

    extra_details = external_api.fetch_enhancement_details(barcode)
    if extra_details is None:
        return jsonify({"error": f"No OpenFoodFacts data found for barcode {barcode}"}), 404

    item.update(extra_details)
    return jsonify(item), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)