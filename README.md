# 🚴 CoolRide: Thermal Comfort Routing for Cyclists

**A Prototype for mitigating Urban Heat Island (UHI) exposure for bike and cycle riders in Singapore.**

### 🌍 Project Overview
CoolRide is an intelligent routing engine that prioritizes **thermal safety** over speed. Unlike standard navigation apps that optimize for distance, CoolRide calculates the **Wet Bulb Globe Temperature (WBGT)** exposure and finds routes that maximize shade coverage.

It uses a "Blue-Green-Grey" infrastructure approach, prioritizing **Park Connectors (PCN)**, **Urban Tree Canopies**, **Water Bodies**, and **Building Shadows** to find the coolest possible path.

---

### 🚀 Key Features (New in V5)

* **💧 Water Body Cooling:** Models evaporative and convective cooling effects from water bodies (reservoirs, lakes) with 100m proximity buffers. Filters significant water features (>0.1 km²) and applies up to 45% thermal cost reduction.
* **☀️ Dynamic Building Shadows:** Calculates real-time shadows cast by buildings based on the sun's exact position (Elevation & Azimuth) and building height data.
* **⏰ Time-Aware Routing:** The optimal route changes throughout the day. A path shaded by buildings at 9 AM might be exposed at 12 PM. CoolRide adapts.
* **🤖 Hybrid AI Engine:** Combines real-time NEA weather data with a custom Linear Regression model (with physics clamping) to forecast heat stress 15 minutes into the future.
* **🌳 Blue-Green Infrastructure:** Integrates **SGTrees** (Canopy), **Park Connectors** (PCN), **Water Bodies** (Cooling effect), and **Building Shadows** for holistic thermal scoring with smart combined discounts (up to 65% reduction for triple coverage).
* **🛡️ Fail-Safe Protocol:** Includes a "Government Override" mode to force maximum safety routes during national heatwave alerts.

---

### 📂 Project Structure

The repository is organized into two main components:

```text
Cool_Route_prototype/
├── data/                        # 💾 Geospatial Data Lake
│   ├── trees.csv                # Urban Tree Canopy Data (Trees.sg)
│   ├── ParkConnectorLoop.geojson # NParks Cycling Path Network
│   ├── HawkerCentresGEOJSON.geojson # Shelter Locations
│   └── water.geojson            # Water Bodies (Reservoirs, Lakes)
│
├── output/                      # ☁️ Live Route Deployments
│   └── latest_route.kml         # The active AI-generated route (Pushed by Python)
│
├── Cool_route_v5.ipynb          # 🧠 The Brain: AI & Spatial Analysis Engine
├── Cool_route_v4.ipynb          # Previous version (Building Shadows)
├── index.html                   # 🗺️ Standalone Leaflet Viewer (For rapid testing)
└── README.md                    # Project Documentation
```


### 📊 Data Sources
* Weather: National Environment Agency (NEA) API ([Real-time WBGT](https://data.gov.sg/datasets?query=wbgt&resultId=d_87884af1f85d702d4f74c6af13b4853d))

* Road Network & Buildings: OpenStreetMap (via OSMnx)

* Vegetation: Trees.sg (Processed via [SGTrees](https://github.com/cheeaun/sgtreesdata/tree/main))

* Infrastructure: [NParks Park Connector Network (GeoJSON)](https://data.gov.sg/datasets/d_a69ef89737379f231d2ae93fd1c5707f/view)

* Blue Spaces: OpenStreetMap Water Features

### 🏃 How to Run (The Engine)
* Open the Colab Notebook (Cool_route_v5.ipynb).

* The code is configured to pull data directly from this repository's /data folder.

* Run all cells. The script will:

* * Calculate sun position and building shadows.

* * Load water body data and create cooling proximity buffers.

* * Fetch live weather from the nearest NEA sensor.

* * Generate a .kml route file in the ```output/``` folder.

* View the Route:

* * Download latest_route.kml and view it in index.html (Leaflet Viewer) or Google My Maps.

### 👥 Team
* Swaminaatha Krishnan
* Arishya Jindal
* Luo Ziyi
* Stefanus Arda 
