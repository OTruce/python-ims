# Inventory Management System

A Flask REST API for a small retail company's admin portal. Employees can
add, view, edit, and delete inventory items, and can pull real product
details from the [OpenFoodFacts API](https://world.openfoodfacts.org/) by
barcode. Includes a CLI client and a full test suite.

## Project Structure

```
inventory-api/
├── app.py              # Flask REST API (CRUD routes)
├── database.py         # Mock in-memory database + helpers
├── external_api.py     # OpenFoodFacts integration
├── cli.py               # Command-line client for the API
├── requirements.txt
├── README.md
└── tests/
    └── test_app.py      # Unit tests (pytest)
```

## Setup

1. Clone the repo and move into it:
   ```bash
   git clone <your-repo-url>
   cd inventory-api
   ```

2. (Recommended) create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

```bash
python app.py
```

The server starts at `http://127.0.0.1:5000`.

## Using the CLI

In a **second terminal** (leave the server running in the first):

```bash
python cli.py
```

You'll get a menu to view, add, edit, delete items, or pull a real
product from OpenFoodFacts by barcode (try `0025293001164` for almond
milk — it's a valid real-world barcode).

## API Reference

| Method | Route | Body | Description |
|---|---|---|---|
| GET | `/items` | — | List all inventory items |
| GET | `/items/<id>` | — | Get one item |
| POST | `/items` | JSON | Create a new item |
| PATCH | `/items/<id>` | JSON | Update fields on an item |
| DELETE | `/items/<id>` | — | Remove an item |
| GET | `/items/fetch/<barcode>` | — | Fetch from OpenFoodFacts, add to inventory |

### Example: create an item

```bash
curl -X POST http://127.0.0.1:5000/items \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Orange Juice", "brands": "Tropicana", "quantity": 10, "price": 4.99}'
```

### Example: fetch by barcode

```bash
curl http://127.0.0.1:5000/items/fetch/0025293001164
```

## Running Tests

```bash
pytest tests/ -v
```

11 tests cover every CRUD route (success and not-found cases) plus the
external API route, mocked with `unittest.mock` so tests don't depend
on internet access.

## Data Model

Each inventory item:

```json
{
  "id": 1,
  "product_name": "Organic Almond Milk",
  "brands": "Silk",
  "barcode": "0025293001164",
  "ingredients_text": "Filtered water, almonds, cane sugar",
  "quantity": 25,
  "price": 3.99
}
```

## Notes / Future Improvements

- Currently the "database" is an in-memory Python list, so data resets
  every time the server restarts. A next step would be swapping in
  SQLite or Postgres via SQLAlchemy.
- No authentication yet — in production, admin routes should require
  a login.
