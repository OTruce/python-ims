"""
tests/test_app.py

Unit tests for the Inventory Management API.

We use Flask's built-in test client, which lets us call our routes
directly in Python without actually starting a server.

For the external-API route, we use unittest.mock to fake
external_api.fetch_product_by_barcode so tests don't depend on
real internet access or OpenFoodFacts being up.
"""

import sys
import os
from unittest.mock import patch

import pytest

# Make sure we can import app.py and database.py from the parent folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as flask_app_module
import database


@pytest.fixture
def client():
    """
    Runs before every test. Gives us a fresh Flask test client and
    resets the mock database to a known state, so tests don't
    interfere with each other.
    """
    flask_app_module.app.config["TESTING"] = True

    # Reset the in-memory database before every test
    database.inventory_db.clear()
    database.inventory_db.extend([
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
    ])

    with flask_app_module.app.test_client() as test_client:
        yield test_client


# ---------- READ tests ----------

def test_get_all_items(client):
    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_single_item_found(client):
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Organic Almond Milk"


def test_get_single_item_not_found(client):
    response = client.get("/items/999")
    assert response.status_code == 404


# ---------- CREATE tests ----------

def test_create_item_success(client):
    payload = {
        "product_name": "Orange Juice",
        "brands": "Tropicana",
        "quantity": 10,
        "price": 4.99,
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert data["product_name"] == "Orange Juice"
    assert data["id"] == 3  # next id after 1 and 2

    # confirm it actually landed in the "database"
    get_response = client.get("/items/3")
    assert get_response.status_code == 200


def test_create_item_missing_name(client):
    response = client.post("/items", json={"brands": "NoName Co."})
    assert response.status_code == 400


# ---------- UPDATE tests ----------

def test_update_item_success(client):
    response = client.patch("/items/1", json={"quantity": 100})
    assert response.status_code == 200
    assert response.get_json()["quantity"] == 100
    # untouched fields should stay the same
    assert response.get_json()["product_name"] == "Organic Almond Milk"


def test_update_item_not_found(client):
    response = client.patch("/items/999", json={"quantity": 5})
    assert response.status_code == 404


# ---------- DELETE tests ----------

def test_delete_item_success(client):
    response = client.delete("/items/1")
    assert response.status_code == 200

    # confirm it's actually gone
    get_response = client.get("/items/1")
    assert get_response.status_code == 404


def test_delete_item_not_found(client):
    response = client.delete("/items/999")
    assert response.status_code == 404


# ---------- EXTERNAL API tests (mocked) ----------

@patch("app.external_api.fetch_product_by_barcode")
def test_fetch_from_external_api_success(mock_fetch, client):
    # Fake what OpenFoodFacts would return, so we don't call the real internet
    mock_fetch.return_value = {
        "product_name": "Mock Cereal",
        "brands": "MockBrand",
        "barcode": "1234567890123",
        "ingredients_text": "Oats, sugar",
        "quantity": 0,
        "price": 0.0,
    }

    response = client.get("/items/fetch/1234567890123")
    assert response.status_code == 201
    assert response.get_json()["product_name"] == "Mock Cereal"

    # it should now be in our own database too
    all_items = client.get("/items").get_json()
    assert len(all_items) == 3


@patch("app.external_api.fetch_product_by_barcode")
def test_fetch_from_external_api_not_found(mock_fetch, client):
    mock_fetch.return_value = None  # simulate barcode not found

    response = client.get("/items/fetch/0000000000000")
    assert response.status_code == 404
