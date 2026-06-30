import requests
import json

API_BASE = "http://127.0.0.1:5000/api"

# Login to get token
login_response = requests.post(f"{API_BASE}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})

if login_response.status_code != 200:
    print("Login failed")
    exit(1)

token = login_response.json()['access_token']
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# TB medicines to add
tb_medicines = [
    {
        "atc_code": "J04AC01",
        "atc_level_1": "J",
        "atc_level_2": "J04",
        "atc_level_3": "J04A",
        "atc_level_4": "J04AC",
        "atc_level_5": "J04AC01",
        "drug_name": "Isoniazid",
        "ddd": 0.3,
        "ddd_unit": "g",
        "administration_route": "Oral"
    },
    {
        "atc_code": "J04AC02",
        "atc_level_1": "J",
        "atc_level_2": "J04",
        "atc_level_3": "J04A",
        "atc_level_4": "J04AC",
        "atc_level_5": "J04AC02",
        "drug_name": "Rifampicin",
        "ddd": 0.6,
        "ddd_unit": "g",
        "administration_route": "Oral"
    },
    {
        "atc_code": "J04AC05",
        "atc_level_1": "J",
        "atc_level_2": "J04",
        "atc_level_3": "J04A",
        "atc_level_4": "J04AC",
        "atc_level_5": "J04AC05",
        "drug_name": "Pyrazinamide",
        "ddd": 2.0,
        "ddd_unit": "g",
        "administration_route": "Oral"
    },
    {
        "atc_code": "J04AC03",
        "atc_level_1": "J",
        "atc_level_2": "J04",
        "atc_level_3": "J04A",
        "atc_level_4": "J04AC",
        "atc_level_5": "J04AC03",
        "drug_name": "Ethambutol",
        "ddd": 1.2,
        "ddd_unit": "g",
        "administration_route": "Oral"
    }
]

# Add medicines
added = 0
for medicine in tb_medicines:
    response = requests.post(f"{API_BASE}/atc-drugs", json=medicine, headers=headers)
    if response.status_code == 201:
        print(f"Added: {medicine['drug_name']}")
        added += 1
    elif response.status_code == 400:
        print(f"Already exists: {medicine['drug_name']}")
    else:
        print(f"Failed to add {medicine['drug_name']}: {response.text}")

print(f"\nAdded {added} TB medicines")

# Get hospitals
hospitals_response = requests.get(f"{API_BASE}/hospitals", headers=headers)
hospitals = hospitals_response.json()['hospitals']

if not hospitals:
    print("No hospitals found. Please create a hospital first.")
    exit(1)

hospital = hospitals[0]
print(f"\nUsing hospital: {hospital['name']} (ID: {hospital['id']})")

# Get ATC drugs to find their IDs
drugs_response = requests.get(f"{API_BASE}/atc-drugs", headers=headers)
drugs = drugs_response.json()['atc_drugs']

# Add to inventory
added_inventory = 0
for medicine in tb_medicines:
    drug = next((d for d in drugs if d['drug_name'] == medicine['drug_name']), None)
    if drug:
        inventory_data = {
            "hospital_id": hospital['id'],
            "atc_drug_id": drug['id'],
            "stock_quantity": 1000,
            "unit_type": "tablets",
            "batch_number": "TB-INITIAL-001",
            "location": "Main Pharmacy"
        }
        response = requests.post(f"{API_BASE}/pharmacy-inventory", json=inventory_data, headers=headers)
        if response.status_code == 201:
            print(f"Added inventory: {drug['drug_name']} (Stock: 1000)")
            added_inventory += 1
        elif response.status_code == 400:
            print(f"Inventory already exists: {drug['drug_name']}")
        else:
            print(f"Failed to add inventory for {drug['drug_name']}: {response.text}")

print(f"\nAdded {added_inventory} TB medicines to pharmacy inventory")
