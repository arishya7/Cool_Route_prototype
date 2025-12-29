#!/usr/bin/env python3
"""
Simple Flask server wrapping Cool_route_v5.3 logic
Full v5.3 features: Trees, Buildings, Water, PCN
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import osmnx as ox
import networkx as nx
import simplekml
import geopandas as gpd
import pandas as pd
import numpy as np
import os
import math
import requests
from datetime import datetime, timedelta
import pytz
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
import pickle
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "methods": ["GET", "POST", "OPTIONS"]}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,ngrok-skip-browser-warning')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# Local data paths (files deployed with Cloud Run)
PCN_URL = "data/ParkConnectorLoop.geojson"
TREES_URL = "data/trees_downloaded.csv"
WATER_URL = "data/water.geojson"
HAWKER_URL = "data/hawker_centres.geojson"

# Thermal weights from v5.3
WEIGHT_PCN = 0.5
WEIGHT_WATER = 0.55
WEIGHT_TREE_SHADE = 0.6
WEIGHT_BUILDING_SHADE = 0.7
WEIGHT_ULTIMATE = 0.35

# AI Weather Cache
CACHE_FILE = "coolride_weather_memory.pkl"

# Sun position calculation (from v5.3)
def calculate_sun_position(latitude, longitude, timestamp):
    """Calculate sun elevation and azimuth"""
    day_of_year = timestamp.timetuple().tm_yday

    # Declination angle
    declination = 23.45 * math.sin(math.radians((360/365) * (day_of_year - 81)))

    # Hour angle
    hour = timestamp.hour + timestamp.minute / 60.0
    hour_angle = 15 * (hour - 12)

    # Sun elevation
    lat_rad = math.radians(latitude)
    dec_rad = math.radians(declination)
    ha_rad = math.radians(hour_angle)

    sin_elev = (math.sin(lat_rad) * math.sin(dec_rad) +
                math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad))
    elevation = math.degrees(math.asin(max(-1, min(1, sin_elev))))

    # Sun azimuth
    cos_azim = ((math.sin(dec_rad) - math.sin(lat_rad) * sin_elev) /
                (math.cos(lat_rad) * math.cos(math.radians(elevation))))
    cos_azim = max(-1, min(1, cos_azim))
    azimuth = math.degrees(math.acos(cos_azim))

    if hour > 12:
        azimuth = 360 - azimuth

    return elevation, azimuth

# Shadow calculation (from v5.3)
def create_shadow_polygon(building_polygon, building_height, sun_elevation, sun_azimuth):
    """Create shadow polygon from building footprint"""
    from shapely.affinity import translate

    if sun_elevation <= 0:
        return None  # Night time

    # Shadow length = height / tan(elevation)
    shadow_length = building_height / math.tan(math.radians(sun_elevation))

    # Shadow direction (opposite of sun)
    shadow_direction = (sun_azimuth + 180) % 360

    # Calculate offset in meters
    shadow_offset_y = shadow_length * math.cos(math.radians(shadow_direction))
    shadow_offset_x = shadow_length * math.sin(math.radians(shadow_direction))

    # Get building centroid
    centroid = building_polygon.centroid
    lat, lon = centroid.y, centroid.x

    # Convert meters to degrees
    deg_per_meter_lat = 1 / 111000
    deg_per_meter_lon = 1 / (111000 * math.cos(math.radians(lat)))

    offset_lat = shadow_offset_y * deg_per_meter_lat
    offset_lon = shadow_offset_x * deg_per_meter_lon

    # Create shadow by translating building polygon
    shadow = translate(building_polygon, xoff=offset_lon, yoff=offset_lat)

    # Union with building for full coverage
    full_shadow = building_polygon.union(shadow).convex_hull

    return full_shadow

# AI Weather Functions (from v5.3)
def get_cache():
    """Load weather data cache"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "rb") as f:
                return pickle.load(f)
        except:
            return {}
    return {}

def save_cache(data):
    """Save weather data cache"""
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(data, f)

def fetch_historical_data(station_name, days_back=3):
    """Fetch historical WBGT data from NEA API"""
    cache = get_cache()
    today_str = datetime.now().strftime("%Y-%m-%d")
    cache_key = f"{station_name}_{today_str}"

    if cache_key in cache and len(cache[cache_key].get('values', [])) > 20:
        print(f"   ⚡ Memory Hit! Loaded {len(cache[cache_key]['values'])} points.")
        return cache[cache_key]['timestamps'], cache[cache_key]['values']

    print(f"   📡 Memory Miss. Analyzing last {days_back} days...")
    all_timestamps, all_values = [], []

    for i in range(days_back + 1):
        target_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        url = "https://api-open.data.gov.sg/v2/real-time/api/weather"
        params = {"api": "wbgt", "date": target_date}

        # PAGINATION LOOP
        while True:
            try:
                resp = requests.get(url, params=params, timeout=5)
                if resp.status_code != 200:
                    break
                data = resp.json()
                if 'data' not in data:
                    break

                for rec in data['data'].get('records', []):
                    dt = datetime.fromisoformat(rec['datetime'])
                    for r in rec['item']['readings']:
                        if r.get('station', {}).get('name') == station_name:
                            val = float(r.get('wbgt') or r.get('value'))
                            mins = dt.hour * 60 + dt.minute
                            now_mins = datetime.now().hour * 60 + datetime.now().minute
                            if abs(mins - now_mins) < 240:  # 4 hour window
                                all_timestamps.append(mins)
                                all_values.append(val)

                token = data['data'].get('paginationToken')
                if token:
                    params['paginationToken'] = token
                else:
                    break
            except:
                break

    if len(all_values) > 20:
        cache[cache_key] = {'timestamps': all_timestamps, 'values': all_values}
        save_cache(cache)
        print(f"   💾 Learned & Saved {len(all_values)} thermal patterns.")

    return all_timestamps, all_values

def predict_trend(station_name, current_wbgt):
    """Predict WBGT trend using linear regression"""
    timestamps, values = fetch_historical_data(station_name)
    if len(values) < 10:
        return current_wbgt, "Stable ➖", "Low Data"

    # Linear Regression
    model = LinearRegression()
    model.fit(np.array(timestamps).reshape(-1, 1), np.array(values))

    # Forecast 15 minutes ahead
    now = datetime.now()
    fut_min = now.hour * 60 + now.minute + 15
    raw_pred = model.predict([[fut_min]])[0]

    # Physics Clamp (max 0.5°C change in 15 min)
    delta = raw_pred - current_wbgt
    if abs(delta) > 0.5:
        final_pred = current_wbgt + (0.5 if delta > 0 else -0.5)
        note = "(Physics Clamped)"
    else:
        final_pred = raw_pred
        note = ""

    trend = "Rising 📈" if final_pred > current_wbgt + 0.1 else "Falling 📉" if final_pred < current_wbgt - 0.1 else "Stable ➖"
    return final_pred, trend, f"High {note}"

def get_nearest_wbgt_station(lat, lon):
    """Find nearest WBGT sensor and get current reading"""
    print("⏳ Connecting to NEA Official WBGT Sensor Network...")
    url = "https://api-open.data.gov.sg/v2/real-time/api/weather"
    try:
        resp = requests.get(url, params={"api": "wbgt"}, timeout=10)
        data = resp.json()
        readings = data['data']['records'][0]['item'].get('readings', [])

        closest_station = "Unknown"
        min_dist = float('inf')
        current_val = None

        for r in readings:
            try:
                loc = {}
                s_name = "Unknown"
                if 'location' in r:
                    loc = r['location']
                elif 'station' in r and 'location' in r['station']:
                    loc = r['station']['location']
                if 'station' in r:
                    s_name = r['station'].get('name', 'Unknown')
                s_lat = float(loc.get('latitude', 0))
                s_lon = float(loc.get('longitude', loc.get('longtitude', 0)))
                if s_lat == 0 or s_lon == 0:
                    continue

                val = r.get('wbgt') or r.get('value')
                if val is None:
                    continue
                val = float(val)
                dist = math.sqrt((lat - s_lat)**2 + (lon - s_lon)**2)

                if dist < min_dist:
                    min_dist = dist
                    closest_station = s_name
                    current_val = val
            except:
                continue

        if current_val is None:
            return 30.0, "System Fallback"
        print(f"   📍 Nearest Sensor: {closest_station} (Dist: {min_dist*111:.2f} km)")
        return current_val, closest_station
    except Exception as e:
        print(f"   ⚠️ WBGT Sensor Fail: {e}. Using Default Safety Value.")
        return 30.0, "System Fallback"

def get_safety_recommendation(wbgt):
    """Get safety recommendation based on WBGT (ISO 7243 standards)"""
    if wbgt < 29:
        return "✅ Safe to Ride", "green", "Normal hydration recommended."
    elif wbgt < 31:
        return "⚠️ CAUTION", "orange", "Seek shade frequently. Increase hydration. Take breaks every 20-30 minutes."
    else:
        return "🛑 HIGH RISK", "red", "Avoid outdoor activities. If riding is essential, take frequent breaks in air-conditioned areas."

# Main route calculation (from v5.3)
def calculate_route_v53(start_lat, start_lon, end_lat, end_lon, departure_time):
    """Full v5.3 route calculation with all features"""

    print(f"⏳ Calculating route from ({start_lat}, {start_lon}) to ({end_lat}, {end_lon})")

    # 1. GET GRAPH - USE PRE-LOADED NETWORK
    try:
        # List of cached networks with their center points
        cached_networks = {
            'tampines': (1.3530, 103.9450, 2000),
            'orchard': (1.3048, 103.8318, 2000),
            'marina_bay': (1.2806, 103.8510, 2000),
            'city_hall': (1.2930, 103.8520, 2000),
            'chinatown': (1.2838, 103.8446, 2000),
            'botanic_gardens': (1.3138, 103.8159, 2000),
            'east_coast_park': (1.3010, 103.9140, 2500),
            'sentosa': (1.2494, 103.8303, 2000),
            'bedok': (1.3236, 103.9273, 2000),
            'pasir_ris': (1.3721, 103.9474, 2000),
            'changi': (1.3644, 103.9915, 2000),
            'bishan': (1.3521, 103.8484, 2000),
            'ang_mo_kio': (1.3691, 103.8454, 2000),
            'clementi': (1.3162, 103.7649, 2000),
            'jurong_east': (1.3329, 103.7436, 2000),
        }

        # Find closest cached network
        G = None
        best_match = None
        min_distance = float('inf')

        for name, (lat, lon, radius) in cached_networks.items():
            filename = f'data/{name}_network.graphml'
            if os.path.exists(filename):
                # Calculate distance from start point to cache center
                import math
                distance = math.sqrt((start_lat - lat)**2 + (start_lon - lon)**2) * 111000  # rough meters
                if distance < radius and distance < min_distance:
                    min_distance = distance
                    best_match = (name, filename)

        if best_match:
            name, filename = best_match
            print(f"   📦 Loading cached {name} network...")
            G = ox.load_graphml(filename)
            print(f"   ✅ Network loaded! ({len(G.nodes)} nodes, {len(G.edges)} edges)")
        else:
            # Fallback to downloading (slow, for other locations)
            print("   🔄 Downloading network from OSM (this may be slow)...")
            G = ox.graph_from_point((start_lat, start_lon), dist=2000, network_type='bike')

        nodes = ox.graph_to_gdfs(G, edges=False)
        miny, maxy = nodes.y.min(), nodes.y.max()
        minx, maxx = nodes.x.min(), nodes.x.max()
        print(f"   📐 Zone Limits: Lat[{miny:.4f}, {maxy:.4f}], Lon[{minx:.4f}, {maxx:.4f}]")
    except Exception as e:
        print(f"   ❌ Network Error: {e}")
        return None, None, None, [], 0, 0

    # 2. LOAD PCN
    print("⏳ Loading Park Connectors...")
    pcn_union = None
    try:
        pcn_data = gpd.read_file(PCN_URL)
        if pcn_data.crs != "EPSG:4326":
            pcn_data = pcn_data.to_crs("EPSG:4326")
        try:
            pcn_union = pcn_data.geometry.union_all()
        except:
            pcn_union = pcn_data.geometry.unary_union
        print(f"   ✅ PCN Loaded")
    except:
        print("   ⚠️ PCN Data missing")

    # 3. LOAD TREES
    print("⏳ Loading Trees...")
    trees_buffer = None
    try:
        # Check if trees CSV exists
        if os.path.exists(TREES_URL):
            trees_df = pd.read_csv(TREES_URL)

            # Verify columns exist
            if 'lat' not in trees_df.columns or 'lng' not in trees_df.columns:
                print(f"   ⚠️ Tree CSV missing columns. Found: {list(trees_df.columns)}")
                print(f"   ⚠️ File size: {os.path.getsize(TREES_URL)} bytes - may be LFS pointer file")
                trees_df = pd.DataFrame()  # Empty DataFrame to skip processing

            # Filter to bounding box only if we have valid data
            if not trees_df.empty and 'lat' in trees_df.columns and 'lng' in trees_df.columns:
                trees_df = trees_df[(trees_df['lat'] >= miny) & (trees_df['lat'] <= maxy) &
                                   (trees_df['lng'] >= minx) & (trees_df['lng'] <= maxx)]

            if not trees_df.empty:
                # Convert to GeoDataFrame
                from shapely.geometry import Point
                geometry = [Point(xy) for xy in zip(trees_df['lng'], trees_df['lat'])]
                trees_gdf = gpd.GeoDataFrame(trees_df, geometry=geometry, crs="EPSG:4326")
                # Convert to projected CRS (SVY21) for accurate buffering
                trees_gdf_proj = trees_gdf.to_crs("EPSG:3414")  # Singapore SVY21
                trees_buffer_proj = trees_gdf_proj.geometry.buffer(10).union_all()  # 10 meters
                # Convert back to WGS84
                trees_buffer = gpd.GeoSeries([trees_buffer_proj], crs="EPSG:3414").to_crs("EPSG:4326")[0]
                print(f"   ✅ Tree shade ({len(trees_gdf)} trees)")
            else:
                print("   ⚠️ No trees in this area or invalid tree data")
        elif os.path.exists('data/Trees_SG.geojson'):
            trees_gdf = gpd.read_file('data/Trees_SG.geojson')
            trees_gdf = trees_gdf.cx[minx:maxx, miny:maxy]
            if not trees_gdf.empty:
                trees_gdf_proj = trees_gdf.to_crs("EPSG:3414")
                trees_buffer_proj = trees_gdf_proj.geometry.buffer(10).union_all()
                trees_buffer = gpd.GeoSeries([trees_buffer_proj], crs="EPSG:3414").to_crs("EPSG:4326")[0]
                print(f"   ✅ Tree shade ({len(trees_gdf)} trees)")
        else:
            print("   ⚠️ Tree data missing (skipping)")
    except Exception as e:
        print(f"   ⚠️ Tree Error: {e}")
        import traceback
        print(f"   ⚠️ Tree Error Details: {traceback.format_exc()}")

    # 4. LOAD BUILDINGS
    print("⏳ Loading Buildings...")
    building_shadows = None
    try:
        buildings_gdf = ox.features_from_point((start_lat, start_lon), tags={'building': True}, dist=2000)
        buildings_gdf = buildings_gdf[buildings_gdf.geometry.type == 'Polygon']
        buildings_gdf['estimated_height'] = 15

        # Calculate Sun Position
        sun_elev, sun_azim = calculate_sun_position(start_lat, start_lon, departure_time)
        print(f"   ☀️ Sun: {sun_elev:.1f}° elev, {sun_azim:.1f}° azim")

        if sun_elev > 0:
            shadow_polygons = []
            for _, building in buildings_gdf.iterrows():
                shadow = create_shadow_polygon(building.geometry, building['estimated_height'], sun_elev, sun_azim)
                if shadow:
                    shadow_polygons.append(shadow)

            building_shadows = unary_union(shadow_polygons)
            print(f"   ✅ Building shadows generated")
        else:
            print("   🌙 Night time (No shadows)")
    except Exception as e:
        print(f"   ⚠️ Building Error: {e}")

    # 5. LOAD WATER
    print("⏳ Loading Water...")
    water_buffer = None
    try:
        if os.path.exists('data/URA_Waterbody.geojson'):
            water_gdf = gpd.read_file('data/URA_Waterbody.geojson')
            water_gdf = water_gdf.cx[minx:maxx, miny:maxy]
            if not water_gdf.empty:
                # Convert to projected CRS for accurate buffering
                water_gdf_proj = water_gdf.to_crs("EPSG:3414")
                water_buffer_proj = water_gdf_proj.geometry.buffer(100).union_all()  # 100 meters
                water_buffer = gpd.GeoSeries([water_buffer_proj], crs="EPSG:3414").to_crs("EPSG:4326")[0]
                print(f"   ✅ Water cooling ({len(water_gdf)} features)")
        else:
            print("   ⚠️ Water data missing (skipping)")
    except Exception as e:
        print(f"   ⚠️ Water Error: {e}")

    # 6. LOAD AMENITIES (Hawker centers, MRT, supermarkets, landmarks)
    print("⏳ Loading Amenities & Landmarks...")
    amenities_list = []
    try:
        # A. Load hawker centers from GitHub (Official NParks dataset - same as v5.3)
        try:
            hawker_gdf = gpd.read_file(HAWKER_URL)
            if hawker_gdf.crs != "EPSG:4326":
                hawker_gdf = hawker_gdf.to_crs("EPSG:4326")
            hawker_gdf = hawker_gdf.cx[minx:maxx, miny:maxy]

            for idx, row in hawker_gdf.iterrows():
                name = row.get('NAME', row.get('name', 'Unknown'))
                if name == 'Unknown':
                    continue
                if row.geometry.geom_type == 'Point':
                    lat, lon = row.geometry.y, row.geometry.x
                else:
                    lat, lon = row.geometry.centroid.y, row.geometry.centroid.x
                amenities_list.append((name, lat, lon, "Hawker"))
            print(f"   ✅ Loaded {len(hawker_gdf)} hawkers from GitHub")
        except Exception as e:
            print(f"   ⚠️ GitHub Hawker Error: {e}, using OSM fallback...")
            # Fallback to OSM if GitHub fails
            tags = {'amenity': ['food_court', 'hawker_centre', 'marketplace']}
            pois = ox.features_from_point((start_lat, start_lon), tags=tags, dist=2000)
            if not pois.empty:
                for idx, row in pois.iterrows():
                    name = row.get('name', 'Unknown')
                    if name == 'Unknown':
                        continue
                    if row.geometry.geom_type == 'Point':
                        lat, lon = row.geometry.y, row.geometry.x
                    else:
                        lat, lon = row.geometry.centroid.y, row.geometry.centroid.x
                    amenities_list.append((name, lat, lon, "Hawker"))

        # B. Skip supermarkets and MRT (too slow on free tier)
        print("   ⚠️ Skipping OSM amenities (optimized for speed)")
        if False:  # Disabled for performance
            shop_pois = ox.features_from_point((start_lat, start_lon), tags={}, dist=2000)
        if False:
            for idx, row in shop_pois.iterrows():
                name = row.get('name', 'Unknown')
                if name == 'Unknown':
                    continue
                if row.geometry.geom_type == 'Point':
                    lat, lon = row.geometry.y, row.geometry.x
                else:
                    lat, lon = row.geometry.centroid.y, row.geometry.centroid.x
                amenities_list.append((name, lat, lon, "Supermarket"))

        # C. Load MRT stations from local file
        try:
            mrt_gdf = gpd.read_file('data/mrt_stations.geojson')
            if mrt_gdf.crs != "EPSG:4326":
                mrt_gdf = mrt_gdf.to_crs("EPSG:4326")
            mrt_gdf = mrt_gdf.cx[minx:maxx, miny:maxy]

            for idx, row in mrt_gdf.iterrows():
                name = row.get('name', 'Unknown')
                if name == 'Unknown':
                    continue
                lat, lon = row.geometry.y, row.geometry.x
                amenities_list.append((name, lat, lon, "MRT"))
            print(f"   ✅ Loaded {len(mrt_gdf)} MRT stations")
        except Exception as e:
            print(f"   ⚠️ MRT Error: {e}")

        # D. Load famous landmarks from local file
        try:
            landmarks_gdf = gpd.read_file('data/landmarks.geojson')
            if landmarks_gdf.crs != "EPSG:4326":
                landmarks_gdf = landmarks_gdf.to_crs("EPSG:4326")
            landmarks_gdf = landmarks_gdf.cx[minx:maxx, miny:maxy]

            for idx, row in landmarks_gdf.iterrows():
                name = row.get('name', 'Unknown')
                if name == 'Unknown':
                    continue
                lat, lon = row.geometry.y, row.geometry.x
                landmark_type = row.get('type', 'Landmark')
                amenities_list.append((name, lat, lon, landmark_type))
            print(f"   ✅ Loaded {len(landmarks_gdf)} landmarks")
        except Exception as e:
            print(f"   ⚠️ Landmarks Error: {e}")

        print(f"   ✅ Total points of interest: {len(amenities_list)}")
    except Exception as e:
        print(f"   ⚠️ Amenities Error: {e}")

    # 6. CALCULATE COST
    print("⏳ Calculating costs...")
    hour = departure_time.hour
    shade_multiplier = 0.6 if (hour < 10 or hour > 16) else 1.0

    for u, v, k, data in G.edges(keys=True, data=True):
        if 'geometry' in data:
            edge_geom = data['geometry']
        else:
            edge_geom = LineString([(G.nodes[u]['x'], G.nodes[u]['y']),
                                   (G.nodes[v]['x'], G.nodes[v]['y'])])

        cost = data['length']

        # Check intersections
        is_pcn = pcn_union and edge_geom.intersects(pcn_union)
        is_tree = trees_buffer and edge_geom.intersects(trees_buffer)
        is_shadow = building_shadows and edge_geom.intersects(building_shadows)
        is_water = water_buffer and edge_geom.intersects(water_buffer)

        # Apply weights
        if is_tree and is_shadow and is_water:
            cost *= WEIGHT_ULTIMATE
        elif is_tree and is_shadow:
            cost *= 0.45
        elif is_water:
            cost *= WEIGHT_WATER
        elif is_tree:
            cost *= WEIGHT_TREE_SHADE
        elif is_shadow:
            cost *= (WEIGHT_BUILDING_SHADE * shade_multiplier)
        elif is_pcn:
            cost *= WEIGHT_PCN

        data['cool_cost'] = cost

    # 7. SOLVE
    orig = ox.distance.nearest_nodes(G, start_lon, start_lat)
    dest = ox.distance.nearest_nodes(G, end_lon, end_lat)

    try:
        r_fast = nx.shortest_path(G, orig, dest, weight='length')
        r_cool = nx.shortest_path(G, orig, dest, weight='cool_cost')

        # Calculate distances by summing edge lengths
        fast_distance = 0
        for u, v in zip(r_fast[:-1], r_fast[1:]):
            fast_distance += G[u][v][0]['length']

        cool_distance = 0
        for u, v in zip(r_cool[:-1], r_cool[1:]):
            cool_distance += G[u][v][0]['length']

        return G, r_fast, r_cool, amenities_list, fast_distance, cool_distance
    except Exception as e:
        print(f"   ❌ Routing failed: {e}")
        return None, None, None, [], 0, 0

@app.route('/calculate_route', methods=['POST', 'OPTIONS'])
def calculate_route():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        data = request.json
        print(f"\n📨 Request: {data}")

        # Get start/end from request
        start_text = data.get('start', 'Tampines MRT')
        end_text = data.get('end', 'Tampines Eco Green')
        time_text = data.get('time', '')

        # Geocode
        print(f"🔍 Geocoding: {start_text} -> {end_text}")
        start_coords = ox.geocode(start_text + ", Singapore")
        end_coords = ox.geocode(end_text + ", Singapore")

        # Parse time
        sgt_zone = pytz.timezone('Asia/Singapore')
        if time_text:
            try:
                hour, minute = map(int, time_text.split(':'))
                departure_time = datetime.now(sgt_zone).replace(hour=hour, minute=minute, second=0)
            except:
                departure_time = datetime.now(sgt_zone)
        else:
            departure_time = datetime.now(sgt_zone)

        # Calculate route using v5.3 logic
        G, r_fast, r_cool, amenities_list, fast_distance, cool_distance = calculate_route_v53(
            start_coords[0], start_coords[1],
            end_coords[0], end_coords[1],
            departure_time
        )

        if G is None or r_fast is None:
            return jsonify({"status": "error", "message": "Route calculation failed"}), 500

        # Convert to KML
        kml = simplekml.Kml()

        def route_to_kml(route, color, name, desc):
            coords = []
            for u, v in zip(route[:-1], route[1:]):
                edge_data = G.get_edge_data(u, v)[0]
                if 'geometry' in edge_data:
                    xs, ys = edge_data['geometry'].xy
                    coords.extend([(float(x), float(y)) for x, y in zip(xs, ys)])
                else:
                    coords.append((float(G.nodes[u]['x']), float(G.nodes[u]['y'])))
                    coords.append((float(G.nodes[v]['x']), float(G.nodes[v]['y'])))

            ls = kml.newlinestring(name=name)
            ls.coords = coords
            ls.style.linestyle.color = color
            ls.style.linestyle.width = 5
            ls.description = desc

        # Check similarity
        set_fast = set(r_fast)
        set_cool = set(r_cool)
        similarity = len(set_fast.intersection(set_cool)) / len(set_fast.union(set_cool))

        print(f"   🔍 Similarity: {similarity*100:.1f}%")

        # Calculate durations for display
        CYCLING_SPEED_KMH = 15
        CYCLING_SPEED_MS = CYCLING_SPEED_KMH * 1000 / 3600

        fast_duration_seconds = fast_distance / CYCLING_SPEED_MS
        cool_duration_seconds = cool_distance / CYCLING_SPEED_MS

        fast_duration_str = f"{int(fast_duration_seconds // 60)}:{int(fast_duration_seconds % 60):02d}"
        cool_duration_str = f"{int(cool_duration_seconds // 60)}:{int(cool_duration_seconds % 60):02d}"

        if similarity > 0.90:
            # Routes are similar - show only cool route
            route_to_kml(r_cool, simplekml.Color.green, "Recommended Route",
                        f"<b>Smart Choice</b><br>The fastest path is also the coolest!<br><br>📏 Distance: {cool_distance:.0f}m ({cool_distance/1000:.1f} km)<br>⏱️ Time: {cool_duration_str} min")
        else:
            # Show both routes
            route_to_kml(r_fast, simplekml.Color.red, "Fastest Route",
                        f"<b>Direct Path</b><br>Shortest time, higher exposure<br><br>📏 Distance: {fast_distance:.0f}m ({fast_distance/1000:.1f} km)<br>⏱️ Time: {fast_duration_str} min")
            route_to_kml(r_cool, simplekml.Color.green, "Cool Route",
                        f"<b>Shaded Path</b><br>More shade, slightly longer<br><br>📏 Distance: {cool_distance:.0f}m ({cool_distance/1000:.1f} km)<br>⏱️ Time: {cool_duration_str} min")

        # Add amenities to KML
        for name, lat, lon, type_label in amenities_list:
            # Map type to emoji
            emoji_map = {
                "Hawker": "🍜",
                "Supermarket": "🛒",
                "MRT": "🚇"
            }
            emoji = emoji_map.get(type_label, "📍")

            p = kml.newpoint(name=f"{emoji} {name}")
            p.coords = [(lon, lat)]
            p.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png'
            p.description = f"<b>{type_label}</b><br>{name}"

        # GET WEATHER DATA & AI PREDICTION
        print("\n🌡️ Fetching Real-Time Weather Data...")
        current_wbgt, station_name = get_nearest_wbgt_station(start_coords[0], start_coords[1])
        pred_wbgt, trend, confidence = predict_trend(station_name, current_wbgt)
        effective_wbgt = max(current_wbgt, pred_wbgt)

        # SAFETY RECOMMENDATION
        safety_status, safety_color, safety_advice = get_safety_recommendation(effective_wbgt)

        # Duration already calculated above for KML descriptions
        print(f"\n📊 WEATHER REPORT: {station_name}")
        print(f"   Current WBGT: {current_wbgt}°C")
        print(f"   Forecast (15min): {pred_wbgt:.1f}°C ({trend})")
        print(f"   Safety: {safety_status}")
        print(f"\n📏 ROUTE STATS:")
        print(f"   Fast Route: {fast_distance:.0f}m ({fast_duration_str})")
        print(f"   Cool Route: {cool_distance:.0f}m ({cool_duration_str})")
        print("✅ Route generated successfully!\n")

        # Build comprehensive insight
        route_insight = f"🟢 Green route is cooler with {int((1 - similarity) * 100)}% more shade. 🔴 Red route is faster but more sun exposure."
        full_insight = f"{route_insight}\n\n{safety_status}: {safety_advice}"

        return jsonify({
            "status": "success",
            "kml_data": kml.kml(),
            "meta": {
                "start_point": start_coords,
                "end_point": end_coords,
                "similarity": f"{similarity*100:.1f}%",
                "weather_station": station_name,
                "fast_distance": f"{fast_distance:.0f}",
                "cool_distance": f"{cool_distance:.0f}",
                "fast_duration": fast_duration_str,
                "cool_duration": cool_duration_str
            },
            "ai_data": {
                "current_temp": f"{current_wbgt:.1f}",
                "forecast_temp": f"{pred_wbgt:.1f}",
                "trend": trend,
                "confidence": confidence,
                "insight": full_insight,
                "safety_status": safety_status,
                "safety_color": safety_color,
                "safety_advice": safety_advice,
                "color": safety_color,
                "shade_gain": int((1 - similarity) * 100)
            }
        })

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SIMPLE COOLRIDE SERVER")
    print("📡 URL: http://localhost:5001")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=False)
