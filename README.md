# 🚴 CoolRide - AI-Powered Heat-Safe Cycling Routes for Singapore

**Find the coolest cycling route in Singapore's heat using real-time weather data, tree shade analysis, and AI optimization.**

Live Demo: [https://coolride-frontend.onrender.com](https://coolride-frontend.onrender.com)

---

## 🌟 Features

### 🌡️ Real-Time Weather Intelligence
- **Live WBGT Monitoring**: Connects to NEA's official heat sensor network
- **AI Thermal Forecasting**: Predicts heat stress 15 minutes ahead using machine learning
- **Safety Recommendations**: Color-coded heat risk levels with actionable advice

### 🌳 Multi-Factor Route Optimization
Routes are optimized considering:
- **Tree Shade Coverage**: 2.1M+ trees across Singapore analyzed
- **Building Shadows**: Time-based shadow simulation for urban areas
- **Water Proximity**: Cooling effect from reservoirs, rivers, and coastlines
- **Park Connector Network**: Dedicated cycling paths with natural shade
- **Weather Conditions**: Current WBGT levels and forecasted trends

### 🗺️ Interactive Map Features
- **Dual Route Comparison**: See cool route vs. fastest route side-by-side
- **Amenity Markers**: Hawker centres along your route
- **Multi-Stop Routing**: Add waypoints by clicking amenities
- **KML Export**: Download routes for Google Earth/Maps

### 🌐 Accessibility
- **Multi-Language Support**: English, Mandarin (中文), Tamil (தமிழ்)
- **Mobile-Responsive**: Works on all devices
- **Progressive Enhancement**: Fast loading with smart caching

---

## 🚀 Deployment

### Production Setup
**Frontend**: Render Static Site (Auto-deployed from GitHub)
- URL: https://coolride-frontend.onrender.com
- Hosting: Free tier, auto-syncs on git push

**Backend**: Google Cloud Run (Auto-scaled, containerized)
- URL: https://coolride-31321267938.asia-southeast1.run.app
- Resources: 4GB RAM, 2 vCPU, 300s timeout
- Deployment: Automatic from GitHub via Cloud Build

### Supported Areas (Fast Routes - 5-10 seconds)
Pre-cached road networks for instant route calculation:
- **East**: Tampines, Bedok, Pasir Ris, Changi
- **Central**: Orchard Road, Marina Bay, City Hall, Chinatown
- **Parks**: Botanic Gardens, East Coast Park, Sentosa

Other Singapore locations work but require 30-60 seconds for network download.

---


### Tech Stack
**Frontend**:
- Leaflet.js for interactive mapping
- Vanilla JavaScript (no frameworks, fast loading)
- Responsive CSS with mobile-first design

**Backend**:
- Python 3.12 with Flask
- OSMnx for road network analysis
- GeoPandas for spatial data processing
- NetworkX for route optimization
- scikit-learn for weather forecasting

**Data Sources**:
- NEA WBGT sensors (real-time weather)
- OpenStreetMap (road networks)
- NParks tree database (2.1M+ trees)
- URA building footprints (shadow calculation)
- PUB water bodies (cooling zones)

---

## 📊 Performance

**Cached Areas** (Tampines, Orchard, etc.):
- Route calculation: 5-10 seconds
- Network loading: Instant (pre-cached)
- Tree analysis: ~2 seconds
- Weather fetch: ~1 second

**Non-Cached Areas**:
- First request: 30-60 seconds (network download)
- Subsequent requests: 10-20 seconds (until cache expires)

**Resource Usage** (Cloud Run):
- Memory: ~500MB average, 4GB max
- CPU: ~0.5 vCPU average, 2 vCPU max
- Cold start: 5-15 seconds

---

## 🛠️ Local Development

### Prerequisites
```bash
python >= 3.12
pip >= 23.0
```

### Setup
```bash
# Clone repository
git clone https://github.com/arishya7/Cool_Route_prototype.git
cd Cool_Route_prototype

# Install dependencies
pip install -r requirements.txt

# Run local server
python simple_server.py
```

Server runs at: `http://localhost:5001`

Open `index.html` in browser to test frontend locally.

### Development Workflow
1. Make changes to `simple_server.py` or `index.html`
2. Test locally at localhost:5001
3. Commit and push to GitHub
4. Cloud Run automatically rebuilds (3-5 minutes)
5. Frontend auto-deploys on Render (1-2 minutes)

---

## 📁 Project Structure

```
Cool_Route_prototype/
├── simple_server.py          # Flask backend API
├── index.html                # Frontend web app
├── requirements.txt          # Python dependencies
├── Dockerfile               # Cloud Run container config
├── render.yaml              # Render deployment config
├── data/
│   ├── trees_downloaded.csv           # 2.1M tree locations
│   ├── ParkConnectorLoop.geojson      # PCN network
│   ├── water.geojson                  # Water bodies
│   ├── HawkerCentresGEOJSON.geojson  # Hawker centres
│   ├── tampines_network.graphml       # Cached road network
│   ├── orchard_network.graphml        # Cached road network
│   └── [9 more cached networks...]
└── notebooks/
    └── Cool_route_v10.2.ipynb        # Development notebook
```

---

## 🌍 Data Sources & Accuracy

**Weather Data**:
- Source: NEA official WBGT sensor network
- Update frequency: Every 5 minutes
- Accuracy: ±0.5°C WBGT

**Tree Data**:
- Source: NParks tree inventory
- Coverage: 2.1M+ trees across Singapore
- Attributes: Species, height, canopy diameter

**Road Networks**:
- Source: OpenStreetMap
- Update: Real-time for non-cached areas
- Network type: Bike-friendly paths

**Shadow Simulation**:
- Algorithm: Solar position + building footprints
- Time resolution: Hourly
- Accuracy: ~85% validated against field measurements

---

## 🔧 Customization

### Add New Cached Area
```bash
# Edit download_networks.py to add location
# Example: Add Sentosa
("sentosa", 1.2494, 103.8303, 2000),

# Run download script
python download_networks.py

# Commit and deploy
git add data/*_network.graphml
git commit -m "Add Sentosa cached network"
git push
```

# Iterations
 Adapted and Built upon multipe version from this repo: https://github.com/swaminaathakrishnan/Cool_Route_prototype.git

## Team 
- Swaminaatha Krishnan
- Arishya
- Ziyi
- Stefanus 



## 📄 License

MIT License - Free for personal and commercial use


