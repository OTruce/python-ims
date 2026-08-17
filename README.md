INVENTORY MANAGEMENT SYSTEM

Project Structure
python-ims/
├── app.py             
├── database.py         
├── external_api.py     
├── cli.py              
├── requirements.txt
├── README.md
└── tests/
    └── test_app.py     

SETUP:
1.	Clone the repo and move into it:
git clone https://github.com/OTruce/python-ims
cd python-ims
2.	Install dependencies:
pip install -r requirements.txt
3.	Create and activate virtual environment:
python3 -m venv venv
source venv/bin/activate
4.	Run the tests suite and confirm all 18 tests pass:
pytest tests/ -v
5.	Start the Flask server:
python3 app.py
It should show:  Running on http://127.0.0.1:5000
6.	Leave that terminal running and open a new fresh terminal.
7.	In the new terminal, cd to that same folder : cd python-ims, and again activate the virtual environment: source venv/bin/activate.
8.	Run the cli file in the new terminal to now get the menu:
python3 cli.py
9.	It will provide the CLI menu to use the features:
      1. View all items  # Will provide seed items from the local inventory
      2. View item by ID  # View items in local inventory
      3. Add item manually 
      4. Add item by barcode (OpenFoodFacts)  # Once barcode is obtained, it can be used to add the item to local inventory
      5. Search OpenFoodFacts by product name  # Allows you to search for data from the OpenFoodFacts source
      6. Enhance an existing item with OpenFoodFacts data # Add data on a specific item in inventory with more data from OpenFoodFacts
      7. Edit item 
      8. Delete item 
      9. Exit



Author:
Stephen Njenga