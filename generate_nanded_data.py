import os
import random
import pandas as pd
import numpy as np

os.makedirs("smartdeliver-ai/data", exist_ok=True)

np.random.seed(42)
random.seed(42)

zones = [
    {"area": "Anand Nagar", "lat": 19.1820, "lng": 77.3180, "weight": 0.25, "radius": 0.012},
    {"area": "Taroda Naka", "lat": 19.1670, "lng": 77.2950, "weight": 0.25, "radius": 0.010},
    {"area": "Workshop Corner", "lat": 19.1550, "lng": 77.3100, "weight": 0.20, "radius": 0.008},
    {"area": "CIDCO Nanded", "lat": 19.1380, "lng": 77.3200, "weight": 0.15, "radius": 0.011},
    {"area": "Old Nanded", "lat": 19.1450, "lng": 77.3020, "weight": 0.10, "radius": 0.009},
    {"area": "Vishnupuri", "lat": 19.1120, "lng": 77.2880, "weight": 0.05, "radius": 0.015},
]

num_records = 1000
data = []

dates = pd.date_range(start="2026-08-01", end="2026-09-08").strftime("%Y-%m-%d").tolist()

for i in range(1, num_records + 1):
    zone = random.choices(zones, weights=[z["weight"] for z in zones])[0]
    lat = np.random.normal(zone["lat"], zone["radius"])
    lng = np.random.normal(zone["lng"], zone["radius"])
    
    order_val = int(np.random.choice([499, 799, 1299, 1599, 2499, 3999, 4999], p=[0.2, 0.25, 0.25, 0.15, 0.1, 0.03, 0.02]))
    orders_cnt = random.randint(1, 6)
    dist = round(random.uniform(1.2, 8.5), 1)
    date_val = random.choice(dates)
    
    data.append({
        "order_id": f"ORD{i:04d}",
        "customer_id": f"CUST{random.randint(101, 750):04d}",
        "order_date": date_val,
        "latitude": round(lat, 6),
        "longitude": round(lng, 6),
        "area": zone["area"],
        "order_value": order_val,
        "orders_count": orders_cnt,
        "delivery_distance_km": dist
    })

df_orders = pd.DataFrame(data)

# Add intentional messy rows to test data cleaning pipeline
df_orders = pd.concat([df_orders, df_orders.iloc[[10]]], ignore_index=True)
df_orders.loc[15, "latitude"] = np.nan
df_orders.loc[25, "longitude"] = np.nan
df_orders.loc[35, "latitude"] = 999.0

df_orders.to_csv("smartdeliver-ai/data/customers_orders.csv", index=False)
print(f"Generated customers_orders.csv with {len(df_orders)} rows")

# 1b. Synthetic population dataset
# This is simulated data for analysis and contains no real personal identities.
population_size = 10000
population_rows = []
first_names = ["Aarav", "Aditi", "Aditya", "Ananya", "Arjun", "Isha", "Kavya", "Neha", "Rahul", "Riya", "Sahil", "Sneha", "Tanvi", "Vikram"]
last_names = ["Patil", "Deshmukh", "Jadhav", "Kadam", "Shinde", "Pawar", "Chavan", "Kulkarni", "Joshi", "More"]
occupations = ["Student", "Service", "Business", "Agriculture", "Healthcare", "Education", "Homemaker", "Retired", "Other"]
education_levels = ["Primary", "Secondary", "Higher Secondary", "Graduate", "Postgraduate"]
income_bands = ["Below 2L", "2L-5L", "5L-10L", "10L-20L", "Above 20L"]
languages = ["Marathi", "Hindi", "Urdu", "Marathi/Hindi"]

for person_number in range(1, population_size + 1):
    zone = random.choices(zones, weights=[z["weight"] for z in zones])[0]
    age = int(np.clip(np.random.normal(31, 16), 1, 85))
    gender = random.choices(["Female", "Male", "Other"], weights=[0.49, 0.49, 0.02])[0]
    household_size = int(np.clip(np.random.normal(4.3, 1.6), 1, 10))
    population_rows.append({
        "person_id": f"PERSON{person_number:05d}",
        "household_id": f"HH{((person_number - 1) // household_size) + 1:05d}",
        "area": zone["area"],
        "latitude": round(float(np.random.normal(zone["lat"], zone["radius"])), 6),
        "longitude": round(float(np.random.normal(zone["lng"], zone["radius"])), 6),
        "age": age,
        "gender": gender,
        "occupation": random.choice(occupations),
        "education_level": random.choice(education_levels),
        "annual_income_band": random.choice(income_bands),
        "primary_language": random.choice(languages),
        "household_size": household_size,
        "is_online_shopper": random.choices([True, False], weights=[0.64, 0.36])[0],
    })

population_df = pd.DataFrame(population_rows)
population_df.to_csv("smartdeliver-ai/data/population.csv", index=False)
print(f"Generated population.csv with {len(population_df)} synthetic people")

# 2. Roads dataset
roads = [
    {"road_id": "ROAD_01", "road_name": "NH-61 (Malegaon Rd)", "latitude": 19.1550, "longitude": 77.3000, "road_type": "National Highway", "road_connectivity_score": 92, "traffic_score": 45, "highway_distance_km": 0.5},
    {"road_id": "ROAD_02", "road_name": "Hingoli Road", "latitude": 19.1750, "longitude": 77.3120, "road_type": "Arterial Road", "road_connectivity_score": 88, "traffic_score": 55, "highway_distance_km": 1.2},
    {"road_id": "ROAD_03", "road_name": "Airport Road", "latitude": 19.1850, "longitude": 77.3250, "road_type": "Secondary Road", "road_connectivity_score": 78, "traffic_score": 30, "highway_distance_km": 2.1},
    {"road_id": "ROAD_04", "road_name": "CIDCO Main Expressway", "latitude": 19.1350, "longitude": 77.3180, "road_type": "Arterial Road", "road_connectivity_score": 85, "traffic_score": 40, "highway_distance_km": 1.8},
    {"road_id": "ROAD_05", "road_name": "Vasmat Road", "latitude": 19.1650, "longitude": 77.2900, "road_type": "State Highway", "road_connectivity_score": 90, "traffic_score": 60, "highway_distance_km": 0.8},
    {"road_id": "ROAD_06", "road_name": "Degloor Naka Bypass", "latitude": 19.1280, "longitude": 77.3050, "road_type": "Bypass Highway", "road_connectivity_score": 86, "traffic_score": 35, "highway_distance_km": 0.4},
]
pd.DataFrame(roads).to_csv("smartdeliver-ai/data/roads.csv", index=False)
print("Generated roads.csv")

# 3. Delivery Centers dataset (Existing centers)
centers = [
    {"center_id": "DC01", "center_name": "CIDCO Logistics Hub", "latitude": 19.1320, "longitude": 77.3150, "capacity_per_day": 2500, "current_daily_orders": 2150, "operating_cost": 145000, "status": "Near Capacity"},
    {"center_id": "DC02", "center_name": "Workshop Zone Depot", "latitude": 19.1580, "longitude": 77.3060, "capacity_per_day": 3000, "current_daily_orders": 2890, "operating_cost": 165000, "status": "Overloaded"},
]
pd.DataFrame(centers).to_csv("smartdeliver-ai/data/delivery_centers.csv", index=False)
print("Generated delivery_centers.csv")

# 4. Locations dataset (Key candidate areas / commercial nodes)
locations = [
    {"location_id": "LOC01", "area": "Anand Nagar Commercial Zone", "latitude": 19.1810, "longitude": 77.3160, "population_density": 14500, "commercial_density": 85, "residential_density": 65, "operating_cost": 135000, "highway_distance_km": 1.5},
    {"location_id": "LOC02", "area": "Taroda Naka Logistics Hub", "latitude": 19.1680, "longitude": 77.2940, "population_density": 16200, "commercial_density": 90, "residential_density": 70, "operating_cost": 125000, "highway_distance_km": 0.9},
    {"location_id": "LOC03", "area": "Workshop Junction South", "latitude": 19.1530, "longitude": 77.3080, "population_density": 18500, "commercial_density": 95, "residential_density": 80, "operating_cost": 155000, "highway_distance_km": 0.6},
    {"location_id": "LOC04", "area": "CIDCO Sector 4 Center", "latitude": 19.1400, "longitude": 77.3220, "population_density": 12000, "commercial_density": 60, "residential_density": 85, "operating_cost": 110000, "highway_distance_km": 1.7},
    {"location_id": "LOC05", "area": "Old Nanded Station Road", "latitude": 19.1460, "longitude": 77.3010, "population_density": 21000, "commercial_density": 92, "residential_density": 90, "operating_cost": 160000, "highway_distance_km": 1.1},
    {"location_id": "LOC06", "area": "Vasmat Road Bypass Plot", "latitude": 19.1720, "longitude": 77.2890, "population_density": 9800, "commercial_density": 50, "residential_density": 55, "operating_cost": 95000, "highway_distance_km": 0.4},
    {"location_id": "LOC07", "area": "Vishnupuri Tech Hub", "latitude": 19.1150, "longitude": 77.2870, "population_density": 7500, "commercial_density": 40, "residential_density": 45, "operating_cost": 85000, "highway_distance_km": 1.2},
]
pd.DataFrame(locations).to_csv("smartdeliver-ai/data/locations.csv", index=False)
print("Generated locations.csv")
