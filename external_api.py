import requests

PRODUCT_URL = "https://world.openfoodfacts.org/api/v2/product"
SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

# OpenFoodFacts requires a descriptive User-Agent identifying your app
# and rejects requests using generic/default headers (they'll return a
# 403 Forbidden otherwise). See their API usage guidelines.
HEADERS = {
    "User-Agent": "InventoryManagementLab/1.0 (student project; contact@example.com)"
}


def _product_dict_from_api(product, barcode=""):
    """
    Shared helper: takes OpenFoodFacts' raw 'product' object and
    reshapes it into the fields OUR database cares about. Both
    fetch_product_by_barcode and fetch_product_by_name end up
    calling this, so the shape stays consistent everywhere.
    """
    return {
        "product_name": product.get("product_name", "Unknown product"),
        "brands": product.get("brands", "Unknown brand"),
        "barcode": product.get("code", barcode),
        "ingredients_text": product.get("ingredients_text", ""),
        "quantity": 0,   # new stock starts at 0 until an employee sets it
        "price": 0.0,    # price isn't in OpenFoodFacts, employee sets it
    }


def fetch_product_by_barcode(barcode):
    """
    Calls OpenFoodFacts for a given barcode.
    """
    url = f"{PRODUCT_URL}/{barcode}.json"

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Error contacting OpenFoodFacts: {error}")
        return None

    data = response.json()

    # OpenFoodFacts returns status: 0 when the barcode isn't found
    if data.get("status") != 1:
        return None

    return _product_dict_from_api(data.get("product", {}), barcode=barcode)


def fetch_product_by_name(name, limit=5):
    """
    Searches OpenFoodFacts by product name
    """
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit,
    }

    try:
        response = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=5)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Error contacting OpenFoodFacts: {error}")
        return []

    data = response.json()
    raw_products = data.get("products", [])

    return [_product_dict_from_api(p) for p in raw_products if p.get("product_name")]


def fetch_enhancement_details(barcode):
    """
    Used to ENHANCE an item we already have in our inventory.
    Given a barcode, pulls extra descriptive fields from
    OpenFoodFacts that our own manually-entered items usually
    don't have (ingredients, categories, nutrition grade, image).

    Returns a dict of extra fields to merge into an existing item,
    or None if the barcode wasn't found.
    """
    url = f"{PRODUCT_URL}/{barcode}.json"

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Error contacting OpenFoodFacts: {error}")
        return None

    data = response.json()
    if data.get("status") != 1:
        return None

    product = data.get("product", {})

    # Only return fields that are genuinely "extra" enrichment data, so we don't clobber quantity/price the employee already set.
    return {
        "ingredients_text": product.get("ingredients_text", ""),
        "categories": product.get("categories", ""),
        "nutrition_grade": product.get("nutrition_grades", ""),
        "image_url": product.get("image_url", ""),
    }