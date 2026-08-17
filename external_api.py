"""
external_api.py

Handles all communication with the OpenFoodFacts API.
Keeping this in its own module means:
  1. app.py stays focused on OUR api, not someone else's.
  2. We can easily mock/fake this module in unit tests, so our
     tests don't depend on the internet being available.
"""

import requests

BASE_URL = "https://world.openfoodfacts.org/api/v2/product"


def fetch_product_by_barcode(barcode):
    """
    Calls OpenFoodFacts for a given barcode.

    Returns a dict shaped for OUR database on success, or None if
    the product wasn't found / the request failed.
    """
    url = f"{BASE_URL}/{barcode}.json"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Error contacting OpenFoodFacts: {error}")
        return None

    data = response.json()

    # OpenFoodFacts returns status: 0 when the barcode isn't found
    if data.get("status") != 1:
        return None

    product = data.get("product", {})

    return {
        "product_name": product.get("product_name", "Unknown product"),
        "brands": product.get("brands", "Unknown brand"),
        "barcode": barcode,
        "ingredients_text": product.get("ingredients_text", ""),
        "quantity": 0,   # new stock starts at 0 until an employee sets it
        "price": 0.0,    # price isn't in OpenFoodFacts, employee sets it
    }
