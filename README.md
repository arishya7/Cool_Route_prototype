# 🚀 **CoolRide V9.1: The "Global Edition" Engine**
### *Live AI. Multi-Language. Production-Ready.*

---

### **🌍 Project Overview**
CoolRide V9.1 is the fully realized **"Digital Twin"** of Singapore's urban heat profile. It combines real-time shadow simulation, tree canopy analysis, and blue infrastructure cooling to find the safest, coolest path for cyclists.

Unlike early prototypes, V9.1 is a **Live Distributed System**. It runs the heavy AI computation on a cloud GPU/CPU (Colab), exposes a secure API tunnel (Ngrok), and serves a responsive, multi-language web application to any device instantly.

---

### **🔥 What's New in V9.1? (The "Global Launch" Update)**

1.  **⚡ Live API Server (Ngrok Tunnel):**
    * **Old Way:** Static file uploads (Slow, 1-minute delay).
    * **V9 Way:** A real-time Flask API. Click "Route" on the web app, and the Python engine computes it instantly.

2.  **🤖 Physics-Informed AI Forecasting:**
    * **New Feature:** A Diurnal Cycle Model (Sine Wave Regression) that predicts heat stress 1 hour into the future based on the sun's position and current sensor data.

3.  **🛑 Interactive Multi-Stop Routing:**
    * **New Feature:** Users can click on **Hawker Centres (🍜)** or **Supermarkets (🛒)** along the route to instantly add a "Pit Stop." The engine seamlessly stitches the coolest path to the stop and then to the destination.

4.  **🌐 Global Accessibility Suite:**
    * **Multi-Language:** Instantly toggle between **English**, **Mandarin (中文)**, and **Tamil (தமிழ்)**.
    * **Smart Caching:** Instant "Undo" functionality when removing stops.
    * **Data Export:** Download routes as `.kml` for use in Google Earth/Maps.

---

### **🏗️ System Architecture**

`[ 📱 Web App (Frontend) ]`  <--->  `[ 🚇 Ngrok Secure Tunnel ]`  <--->  `[ 🧠 Python AI Server (Backend) ]`

1.  **Request:** User selects Start/End on the website.
2.  **Compute:** Python Engine calculates Shadows, Trees, Water, and AI Weather trends.
3.  **Response:** Server returns a JSON payload with the Route (KML), Amenities, and AI Forecast.
4.  **Render:** The Web App draws the route, amenities, and forecast card in < 200ms.

---

### **🏃 How to Run the Demo**

**Step 1: Launch the Brain**
* In [this notebook](https://github.com/swaminaathakrishnan/Cool_Route_prototype/blob/master/notebooks/Cool_route_v9.1.ipynb), click **Runtime -> Run All**.
* Scroll to the bottom of **Module 7**.
* Copy the public URL: `https://xxxx-xxxx.ngrok-free.app`

**Step 2: Connect the Interface**
* Open the [Live Dashboard](https://swaminaathakrishnan.github.io/Cool_Route_prototype/).
* Paste the URL into the **"Server Connection"** box.

**Step 3: Impress**
* Click **"Find Cool Route"**.
* **Demo the AI:** Show the "AI Thermal Forecast" card.
* **Demo the Interactivity:** Click a Hawker Centre icon -> "Add Stop".
* **Demo the Polish:** Switch Language to Tamil/Mandarin.

---

### **👥 Credits**
* **Swaminaatha Krishnan:** System Architect & Full-Stack Integration
* **Arishya Jindal:** Algorithm Lead (Shadows & Spatial Intelligence)
