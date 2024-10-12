import json
import math

# Load ports data
with open("data/ports.json", "r") as json_file:
    ports = json.load(json_file)  # Load JSON data into a variable

sea_routes = []

# Function to calculate distance using Haversine formula
def haversine(coord1, coord2):
    R = 6371  # Radius of the Earth in kilometers
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c  # Distance in kilometers
    return distance

def estimate_co2_emission(distance, co2_per_km=0.025):
    return distance * co2_per_km

def calculate_cost(distance, cost_per_km=0.00402):
    return distance * cost_per_km # SGD

# Loop through each pair of ports and calculate estimates
for i in range(len(ports)):
    for j in range(i + 1, len(ports)):
        from_port = ports[i]
        to_port = ports[j]

        # Check if the ports are in different countries
        if from_port["country"] != to_port["country"]:
            # Get coordinates
            coord_from = (from_port["coordinates"]["latitude"], from_port["coordinates"]["longitude"])
            coord_to = (to_port["coordinates"]["latitude"], to_port["coordinates"]["longitude"])

            # Calculate distance
            distance = haversine(coord_from, coord_to)

            # Estimate CO2 emissions and cost
            co2_emission = estimate_co2_emission(distance)
            cost = calculate_cost(distance)

            # Create route entry
            route_entry = {
                "location1": from_port["UNLOCODE"],
                "location2": to_port["UNLOCODE"],
                "co2_emission": co2_emission,
                "distance": distance,
                "cost": cost,
            }

            # Append route to sea_routes list
            sea_routes.append(route_entry)

# Save the routes to sea_routes.json
with open("data/sea_routes.json", "w") as json_file:
    json.dump(sea_routes, json_file, indent=4)

print("Sea routes JSON created successfully!")
