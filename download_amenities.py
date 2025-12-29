#!/usr/bin/env python3
"""
Download official Singapore amenities data (MRT stations and landmarks).
"""

import json
import geopandas as gpd
from shapely.geometry import Point

# Singapore MRT/LRT Stations (manually curated list with coordinates)
mrt_stations = [
    # North-South Line (Red)
    {"name": "Jurong East", "line": "NS1/EW24", "lat": 1.3332, "lon": 103.7422},
    {"name": "Bukit Batok", "line": "NS2", "lat": 1.3490, "lon": 103.7497},
    {"name": "Bukit Gombak", "line": "NS3", "lat": 1.3587, "lon": 103.7517},
    {"name": "Choa Chu Kang", "line": "NS4/BP1", "lat": 1.3854, "lon": 103.7443},
    {"name": "Yew Tee", "line": "NS5", "lat": 1.3974, "lon": 103.7473},
    {"name": "Kranji", "line": "NS7", "lat": 1.4251, "lon": 103.7619},
    {"name": "Marsiling", "line": "NS8", "lat": 1.4326, "lon": 103.7740},
    {"name": "Woodlands", "line": "NS9/TE2", "lat": 1.4370, "lon": 103.7865},
    {"name": "Admiralty", "line": "NS10", "lat": 1.4406, "lon": 103.8009},
    {"name": "Sembawang", "line": "NS11", "lat": 1.4491, "lon": 103.8202},
    {"name": "Canberra", "line": "NS12", "lat": 1.4430, "lon": 103.8297},
    {"name": "Yishun", "line": "NS13", "lat": 1.4294, "lon": 103.8350},
    {"name": "Khatib", "line": "NS14", "lat": 1.4172, "lon": 103.8329},
    {"name": "Yio Chu Kang", "line": "NS15", "lat": 1.3817, "lon": 103.8450},
    {"name": "Ang Mo Kio", "line": "NS16", "lat": 1.3699, "lon": 103.8495},
    {"name": "Bishan", "line": "NS17/CC15", "lat": 1.3509, "lon": 103.8484},
    {"name": "Braddell", "line": "NS18", "lat": 1.3406, "lon": 103.8467},
    {"name": "Toa Payoh", "line": "NS19", "lat": 1.3327, "lon": 103.8476},
    {"name": "Novena", "line": "NS20", "lat": 1.3204, "lon": 103.8438},
    {"name": "Newton", "line": "NS21/DT11", "lat": 1.3127, "lon": 103.8384},
    {"name": "Orchard", "line": "NS22/TE14", "lat": 1.3041, "lon": 103.8320},
    {"name": "Somerset", "line": "NS23", "lat": 1.3005, "lon": 103.8390},
    {"name": "Dhoby Ghaut", "line": "NS24/NE6/CC1", "lat": 1.2990, "lon": 103.8456},
    {"name": "City Hall", "line": "NS25/EW13", "lat": 1.2930, "lon": 103.8522},
    {"name": "Raffles Place", "line": "NS26/EW14", "lat": 1.2841, "lon": 103.8515},
    {"name": "Marina Bay", "line": "NS27/CE2/TE20", "lat": 1.2762, "lon": 103.8543},
    {"name": "Marina South Pier", "line": "NS28", "lat": 1.2711, "lon": 103.8630},

    # East-West Line (Green)
    {"name": "Pasir Ris", "line": "EW1", "lat": 1.3730, "lon": 103.9493},
    {"name": "Tampines", "line": "EW2/DT32", "lat": 1.3535, "lon": 103.9451},
    {"name": "Simei", "line": "EW3", "lat": 1.3434, "lon": 103.9533},
    {"name": "Tanah Merah", "line": "EW4/CG", "lat": 1.3276, "lon": 103.9464},
    {"name": "Bedok", "line": "EW5", "lat": 1.3240, "lon": 103.9301},
    {"name": "Kembangan", "line": "EW6", "lat": 1.3212, "lon": 103.9133},
    {"name": "Eunos", "line": "EW7", "lat": 1.3198, "lon": 103.9034},
    {"name": "Paya Lebar", "line": "EW8/CC9", "lat": 1.3177, "lon": 103.8926},
    {"name": "Aljunied", "line": "EW9", "lat": 1.3164, "lon": 103.8823},
    {"name": "Kallang", "line": "EW10", "lat": 1.3115, "lon": 103.8714},
    {"name": "Lavender", "line": "EW11", "lat": 1.3075, "lon": 103.8631},
    {"name": "Bugis", "line": "EW12/DT14", "lat": 1.3002, "lon": 103.8556},
    {"name": "Tanjong Pagar", "line": "EW15", "lat": 1.2764, "lon": 103.8457},
    {"name": "Outram Park", "line": "EW16/NE3/TE17", "lat": 1.2803, "lon": 103.8395},
    {"name": "Tiong Bahru", "line": "EW17", "lat": 1.2862, "lon": 103.8270},
    {"name": "Redhill", "line": "EW18", "lat": 1.2896, "lon": 103.8168},
    {"name": "Queenstown", "line": "EW19", "lat": 1.2942, "lon": 103.8058},
    {"name": "Commonwealth", "line": "EW20", "lat": 1.3025, "lon": 103.7977},
    {"name": "Buona Vista", "line": "EW21/CC22", "lat": 1.3071, "lon": 103.7904},
    {"name": "Dover", "line": "EW22", "lat": 1.3112, "lon": 103.7786},
    {"name": "Clementi", "line": "EW23", "lat": 1.3150, "lon": 103.7652},
    {"name": "Chinese Garden", "line": "EW25", "lat": 1.3425, "lon": 103.7325},
    {"name": "Lakeside", "line": "EW26", "lat": 1.3444, "lon": 103.7208},
    {"name": "Boon Lay", "line": "EW27", "lat": 1.3388, "lon": 103.7059},
    {"name": "Pioneer", "line": "EW28", "lat": 1.3375, "lon": 103.6974},
    {"name": "Joo Koon", "line": "EW29", "lat": 1.3277, "lon": 103.6783},
    {"name": "Gul Circle", "line": "EW30", "lat": 1.3195, "lon": 103.6605},
    {"name": "Tuas Crescent", "line": "EW31", "lat": 1.3212, "lon": 103.6493},
    {"name": "Tuas West Road", "line": "EW32", "lat": 1.3299, "lon": 103.6397},
    {"name": "Tuas Link", "line": "EW33", "lat": 1.3404, "lon": 103.6367},

    # Circle Line (Yellow/Orange)
    {"name": "HarbourFront", "line": "NE1/CC29", "lat": 1.2653, "lon": 103.8219},
    {"name": "Chinatown", "line": "NE4/DT19", "lat": 1.2844, "lon": 103.8438},
    {"name": "Farrer Road", "line": "CC20", "lat": 1.3171, "lon": 103.8074},
    {"name": "Botanic Gardens", "line": "CC19/DT9", "lat": 1.3227, "lon": 103.8156},
    {"name": "Marymount", "line": "CC16", "lat": 1.3488, "lon": 103.8394},
    {"name": "Serangoon", "line": "NE12/CC13", "lat": 1.3498, "lon": 103.8736},
    {"name": "Bartley", "line": "CC12", "lat": 1.3424, "lon": 103.8795},
    {"name": "Tai Seng", "line": "CC11", "lat": 1.3357, "lon": 103.8880},
    {"name": "MacPherson", "line": "CC10/DT26", "lat": 1.3266, "lon": 103.8900},
    {"name": "Nicoll Highway", "line": "CC5", "lat": 1.2999, "lon": 103.8634},
    {"name": "Stadium", "line": "CC6", "lat": 1.3029, "lon": 103.8753},
    {"name": "Mountbatten", "line": "CC7", "lat": 1.3065, "lon": 103.8823},
    {"name": "Dakota", "line": "CC8", "lat": 1.3082, "lon": 103.8881},
    {"name": "Esplanade", "line": "CC3", "lat": 1.2934, "lon": 103.8555},
    {"name": "Promenade", "line": "CC4/DT15", "lat": 1.2930, "lon": 103.8611},
    {"name": "Bras Basah", "line": "CC2", "lat": 1.2975, "lon": 103.8508},

    # Downtown Line (Blue)
    {"name": "Bukit Panjang", "line": "DT1/BP6", "lat": 1.3792, "lon": 103.7619},
    {"name": "Cashew", "line": "DT2", "lat": 1.3693, "lon": 103.7642},
    {"name": "Hillview", "line": "DT3", "lat": 1.3628, "lon": 103.7676},
    {"name": "Beauty World", "line": "DT5", "lat": 1.3411, "lon": 103.7758},
    {"name": "King Albert Park", "line": "DT6", "lat": 1.3353, "lon": 103.7834},
    {"name": "Sixth Avenue", "line": "DT7", "lat": 1.3308, "lon": 103.7969},
    {"name": "Tan Kah Kee", "line": "DT8", "lat": 1.3259, "lon": 103.8075},
    {"name": "Stevens", "line": "DT10/TE11", "lat": 1.3199, "lon": 103.8256},
    {"name": "Rochor", "line": "DT13", "lat": 1.3040, "lon": 103.8523},
    {"name": "Little India", "line": "DT12/NE7", "lat": 1.3068, "lon": 103.8495},
    {"name": "Bendemeer", "line": "DT23", "lat": 1.3141, "lon": 103.8620},
    {"name": "Geylang Bahru", "line": "DT24", "lat": 1.3213, "lon": 103.8716},
    {"name": "Mattar", "line": "DT25", "lat": 1.3266, "lon": 103.8831},
    {"name": "Ubi", "line": "DT27", "lat": 1.3300, "lon": 103.8996},
    {"name": "Kaki Bukit", "line": "DT28", "lat": 1.3348, "lon": 103.9080},
    {"name": "Bedok North", "line": "DT29", "lat": 1.3347, "lon": 103.9176},
    {"name": "Bedok Reservoir", "line": "DT30", "lat": 1.3361, "lon": 103.9334},
    {"name": "Tampines West", "line": "DT31", "lat": 1.3455, "lon": 103.9382},
    {"name": "Tampines East", "line": "DT33", "lat": 1.3565, "lon": 103.9545},
    {"name": "Upper Changi", "line": "DT34", "lat": 1.3416, "lon": 103.9614},
    {"name": "Expo", "line": "DT35/CG1", "lat": 1.3350, "lon": 103.9614},

    # North-East Line (Purple)
    {"name": "Punggol", "line": "NE17/PTC", "lat": 1.4053, "lon": 103.9024},
    {"name": "Sengkang", "line": "NE16/STC", "lat": 1.3916, "lon": 103.8954},
    {"name": "Buangkok", "line": "NE15", "lat": 1.3829, "lon": 103.8930},
    {"name": "Hougang", "line": "NE14", "lat": 1.3713, "lon": 103.8924},
    {"name": "Kovan", "line": "NE13", "lat": 1.3609, "lon": 103.8850},
    {"name": "Boon Keng", "line": "NE9", "lat": 1.3194, "lon": 103.8618},
    {"name": "Potong Pasir", "line": "NE10", "lat": 1.3314, "lon": 103.8687},
    {"name": "Woodleigh", "line": "NE11", "lat": 1.3388, "lon": 103.8708},
    {"name": "Clarke Quay", "line": "NE5", "lat": 1.2886, "lon": 103.8467},

    # Thomson-East Coast Line (Brown)
    {"name": "Napier", "line": "TE12", "lat": 1.3042, "lon": 103.8196},
    {"name": "Orchard Boulevard", "line": "TE13", "lat": 1.3015, "lon": 103.8254},
    {"name": "Great World", "line": "TE15", "lat": 1.2931, "lon": 103.8318},
    {"name": "Havelock", "line": "TE16", "lat": 1.2889, "lon": 103.8352},
    {"name": "Maxwell", "line": "TE18", "lat": 1.2808, "lon": 103.8442},
    {"name": "Shenton Way", "line": "TE19", "lat": 1.2788, "lon": 103.8498},
    {"name": "Gardens by the Bay", "line": "TE22", "lat": 1.2791, "lon": 103.8643},
]

# Famous Singapore Landmarks
landmarks = [
    {"name": "Marina Bay Sands", "type": "Hotel & Casino", "lat": 1.2834, "lon": 103.8607},
    {"name": "Gardens by the Bay", "type": "Park", "lat": 1.2816, "lon": 103.8636},
    {"name": "Singapore Flyer", "type": "Observation Wheel", "lat": 1.2893, "lon": 103.8631},
    {"name": "Merlion Park", "type": "Landmark", "lat": 1.2868, "lon": 103.8545},
    {"name": "Sentosa Island", "type": "Resort", "lat": 1.2494, "lon": 103.8303},
    {"name": "Universal Studios Singapore", "type": "Theme Park", "lat": 1.2540, "lon": 103.8239},
    {"name": "Singapore Zoo", "type": "Zoo", "lat": 1.4043, "lon": 103.7900},
    {"name": "Night Safari", "type": "Zoo", "lat": 1.4020, "lon": 103.7897},
    {"name": "River Wonders", "type": "Zoo", "lat": 1.4026, "lon": 103.7903},
    {"name": "Singapore Botanic Gardens", "type": "Park", "lat": 1.3138, "lon": 103.8159},
    {"name": "Changi Airport", "type": "Airport", "lat": 1.3644, "lon": 103.9915},
    {"name": "Jewel Changi Airport", "type": "Shopping", "lat": 1.3592, "lon": 103.9894},
    {"name": "National Museum of Singapore", "type": "Museum", "lat": 1.2967, "lon": 103.8485},
    {"name": "ArtScience Museum", "type": "Museum", "lat": 1.2862, "lon": 103.8596},
    {"name": "Asian Civilisations Museum", "type": "Museum", "lat": 1.2872, "lon": 103.8511},
    {"name": "Fort Canning Park", "type": "Park", "lat": 1.2939, "lon": 103.8467},
    {"name": "East Coast Park", "type": "Park", "lat": 1.3010, "lon": 103.9140},
    {"name": "Pulau Ubin", "type": "Island", "lat": 1.4040, "lon": 103.9670},
    {"name": "Jurong Bird Park", "type": "Bird Park", "lat": 1.3188, "lon": 103.7070},
    {"name": "Singapore Science Centre", "type": "Museum", "lat": 1.3336, "lon": 103.7361},
    {"name": "Haw Par Villa", "type": "Theme Park", "lat": 1.2821, "lon": 103.7817},
    {"name": "Bugis Street", "type": "Shopping", "lat": 1.2998, "lon": 103.8551},
    {"name": "Clarke Quay", "type": "Entertainment", "lat": 1.2902, "lon": 103.8465},
    {"name": "Boat Quay", "type": "Entertainment", "lat": 1.2874, "lon": 103.8490},
    {"name": "Little India", "type": "Cultural District", "lat": 1.3068, "lon": 103.8495},
    {"name": "Chinatown", "type": "Cultural District", "lat": 1.2838, "lon": 103.8446},
    {"name": "Arab Street", "type": "Cultural District", "lat": 1.3013, "lon": 103.8583},
    {"name": "Kampong Glam", "type": "Cultural District", "lat": 1.3026, "lon": 103.8599},
    {"name": "Sultan Mosque", "type": "Mosque", "lat": 1.3026, "lon": 103.8586},
    {"name": "Sri Mariamman Temple", "type": "Temple", "lat": 1.2826, "lon": 103.8449},
    {"name": "Buddha Tooth Relic Temple", "type": "Temple", "lat": 1.2818, "lon": 103.8442},
    {"name": "Thian Hock Keng Temple", "type": "Temple", "lat": 1.2808, "lon": 103.8475},
    {"name": "Esplanade", "type": "Theater", "lat": 1.2900, "lon": 103.8556},
]

print("🚀 Creating Singapore amenities datasets...")

# Convert to GeoDataFrames
mrt_gdf = gpd.GeoDataFrame(
    mrt_stations,
    geometry=[Point(station['lon'], station['lat']) for station in mrt_stations],
    crs="EPSG:4326"
)

landmarks_gdf = gpd.GeoDataFrame(
    landmarks,
    geometry=[Point(lm['lon'], lm['lat']) for lm in landmarks],
    crs="EPSG:4326"
)

# Save as GeoJSON
mrt_gdf.to_file('data/mrt_stations.geojson', driver='GeoJSON')
landmarks_gdf.to_file('data/landmarks.geojson', driver='GeoJSON')

print(f"✅ Saved {len(mrt_stations)} MRT stations to data/mrt_stations.geojson")
print(f"✅ Saved {len(landmarks)} landmarks to data/landmarks.geojson")
print("\n📊 Summary:")
print(f"   MRT Lines: NS (North-South), EW (East-West), CC (Circle), DT (Downtown), NE (North-East), TE (Thomson-East Coast)")
print(f"   Landmarks: Parks, Museums, Cultural Districts, Entertainment, Temples, Shopping")
print("✅ Done!")
