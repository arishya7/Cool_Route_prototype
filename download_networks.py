#!/usr/bin/env python3
"""
Download and cache road networks for popular Singapore areas.
This makes route calculation much faster by pre-loading networks.
"""

import osmnx as ox
import os

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Popular Singapore areas to cache
# Format: (name, latitude, longitude, radius_in_meters)
AREAS = [
    # Already cached
    # ("tampines", 1.3530, 103.9450, 2000),  # Already have this

    # Central/Downtown
    ("orchard", 1.3048, 103.8318, 2000),      # Orchard Road shopping area
    ("marina_bay", 1.2806, 103.8510, 2000),   # Marina Bay, Gardens by the Bay
    ("city_hall", 1.2930, 103.8520, 2000),    # City Hall, Raffles Place
    ("chinatown", 1.2838, 103.8446, 2000),    # Chinatown

    # Parks & Nature
    ("botanic_gardens", 1.3138, 103.8159, 2000),  # Singapore Botanic Gardens
    ("east_coast_park", 1.3010, 103.9140, 2500),  # East Coast Park (larger area)
    ("sentosa", 1.2494, 103.8303, 2000),      # Sentosa Island

    # East
    ("bedok", 1.3236, 103.9273, 2000),        # Bedok town
    ("pasir_ris", 1.3721, 103.9474, 2000),    # Pasir Ris
    ("changi", 1.3644, 103.9915, 2000),       # Changi area

    # North
    ("bishan", 1.3521, 103.8484, 2000),       # Bishan Park
    ("ang_mo_kio", 1.3691, 103.8454, 2000),   # Ang Mo Kio

    # West
    ("clementi", 1.3162, 103.7649, 2000),     # Clementi
    ("jurong_east", 1.3329, 103.7436, 2000),  # Jurong East
]

print("🚀 Starting network download for popular Singapore areas...")
print(f"📦 Will download {len(AREAS)} networks\n")

successful = []
failed = []

for name, lat, lon, radius in AREAS:
    filename = f"data/{name}_network.graphml"

    # Skip if already exists
    if os.path.exists(filename):
        print(f"⏭️  {name}: Already cached, skipping")
        successful.append(name)
        continue

    try:
        print(f"⏳ Downloading {name} network (center: {lat}, {lon}, radius: {radius}m)...")
        G = ox.graph_from_point(
            (lat, lon),
            dist=radius,
            network_type='bike',
            simplify=True
        )

        # Save to file
        ox.save_graphml(G, filename)

        # Get stats
        num_nodes = len(G.nodes)
        num_edges = len(G.edges)
        file_size = os.path.getsize(filename) / (1024 * 1024)  # MB

        print(f"✅ {name}: {num_nodes} nodes, {num_edges} edges, {file_size:.1f} MB")
        successful.append(name)

    except Exception as e:
        print(f"❌ {name}: Failed - {e}")
        failed.append(name)

    print()

print("\n" + "="*60)
print("📊 DOWNLOAD SUMMARY")
print("="*60)
print(f"✅ Successful: {len(successful)}/{len(AREAS)}")
if successful:
    print(f"   {', '.join(successful)}")
print(f"\n❌ Failed: {len(failed)}/{len(AREAS)}")
if failed:
    print(f"   {', '.join(failed)}")

# Calculate total size
total_size = 0
for name, _, _, _ in AREAS:
    filename = f"data/{name}_network.graphml"
    if os.path.exists(filename):
        total_size += os.path.getsize(filename)

print(f"\n💾 Total cache size: {total_size / (1024 * 1024):.1f} MB")
print("="*60)
