import json
import requests
from itertools import combinations
from dotenv import load_dotenv
import os

load_dotenv()

# Load ports data from ports.json
with open('data/ports.json') as f:
    ports_data = json.load(f)

# Define the API key and base URL for the Distance Matrix API
API_KEY = os.getenv('distance_api_key')
BASE_URL = 'https://api.distancematrix.ai/maps/api/distancematrix/json'

# Fuel cost and emission factors
FUEL_COST_PER_LITRE = 2.36  # Cost in currency units per litre
FUEL_CONSUMPTION_L_PER_100KM = 35  # Average fuel consumption in litres per 100 km
CO2_EMISSION_PER_TONNE_KM = 0.105  # CO2 emission factor in kg

# Prepare the results list
results = []

# Function to calculate CO2 emissions
def calculate_co2_emissions(distance_value, weight_tonnes):
    # distance_value is in meters, convert to km
    distance_km = distance_value / 1000  # Convert meters to kilometers
    return distance_km * weight_tonnes * CO2_EMISSION_PER_TONNE_KM  # in kg

# Function to calculate fuel cost
def calculate_fuel_cost(distance_value):
    # distance_value is in meters, convert to km
    distance_km = distance_value / 1000  # Convert meters to kilometers
    fuel_needed = (distance_km * FUEL_CONSUMPTION_L_PER_100KM) / 100  # in litres
    return fuel_needed * FUEL_COST_PER_LITRE  # in currency units

# Generate all combinations of ports to calculate distance between each pair
for port1, port2 in combinations(ports_data, 2):
    # Check if the ports are in different countries
    if port1['country'] != port2['country']:
        origin = f"{port1['coordinates']['latitude']},{port1['coordinates']['longitude']}"
        destination = f"{port2['coordinates']['latitude']},{port2['coordinates']['longitude']}"
        
        # API request to get the distance
        response = requests.get(
            BASE_URL,
            params={
                'origins': origin,
                'destinations': destination,
                'key': API_KEY
            }
        )
        
        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK':
                distance_info = data['rows'][0]['elements'][0]
                if distance_info['status'] == 'OK':
                    distance = distance_info['distance']['text']
                    distance_value = (distance_info['distance']['value'])/1000
                    weight_tonnes = 20  # Example weight for the cargo in tonnes

                    # Calculate CO2 emissions and fuel cost
                    co2_emissions = calculate_co2_emissions(distance_value, weight_tonnes)
                    fuel_cost = calculate_fuel_cost(distance_value)

                else:
                    # Set distance to null if there are zero results
                    distance = None
                    distance_value = None
                    co2_emissions = None
                    fuel_cost = None
                
                results.append({
                    'location1': port1['UNLOCODE'],
                    'location2': port2['UNLOCODE'],
                    'co2_emissions': co2_emissions,  # in kg
                    'distance': distance_value,
                    'cost': fuel_cost  # in currency units
                })
            else:
                print(f"Error fetching data for {port1['port_name']} to {port2['port_name']}: {data['status']}")
        else:
            print(f"Request failed for {port1['port_name']} to {port2['port_name']}: {response.status_code}")

# Save results to land_routes.json
with open('data/land_routes.json', 'w') as f:
    json.dump(results, f, indent=4)

print("Distance calculations, CO2 emissions, and fuel costs completed and saved to land_routes.json")
