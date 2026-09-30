# SmartDeliver AI – Nanded Delivery Intelligence

## 1. Project Overview & Purpose
**SmartDeliver AI** is an AI/data-driven decision-support system for recommending e-commerce delivery-center locations in Nanded, Maharashtra, India (~19.1550° N, 77.3100° E).

The platform evaluates spatial customer demand patterns, applies scikit-learn K-Means clustering, computes WCSS (Inertia) for the Elbow Method and Silhouette scores, synthesizes candidate delivery center sites from cluster centroids and road network nodes, and scores each site using a multi-criteria decision-support engine.

> **Note on Datasets**: All datasets provided in this project (`customers_orders.csv`, `population.csv`, `roads.csv`, `delivery_centers.csv`, and `locations.csv`) are synthetic and illustrative, designed to model realistic operational scenarios for delivery hub optimization in Nanded.

---

## 2. Technology Stack

### Backend
- **Python**: Core programming language
- **FastAPI**: REST API framework serving backend endpoints and static frontend assets
- **Uvicorn**: High-performance ASGI web server

### Frontend
- **HTML5**: Semantic web page structure
- **Vanilla CSS**: Clean, responsive styling and layout system
- **Vanilla JavaScript**: Client-side logic, API communication, and state management
- *(Note: The frontend is purely vanilla HTML/CSS/JS served directly by FastAPI. It does NOT use React, Vite, or external build steps.)*

### ML & Data Science
- **Pandas**: Data loading, cleaning, validation, and aggregations
- **NumPy**: Numerical computations
- **scikit-learn**:
  - `StandardScaler`: Normalization of spatial coordinates
  - `KMeans`: Unsupervised customer spatial clustering
  - Elbow Method / WCSS (Inertia): Evaluating cluster quality across $K=2..8$
  - Silhouette Score: Automated detection of optimal cluster count $K$

### Geospatial & Mapping
- **Haversine Distance**: Calculating customer delivery distances and coverage radii (2km, 5km, 10km)
- **Leaflet.js**: Client-side interactive mapping library
- **OpenStreetMap**: Base map tiles and spatial coordinate references for Nanded

---

## 3. Data Inventory (Synthetic / Illustrative)
The `data/` directory contains:
- `customers_orders.csv`: Synthetic customer records with order frequencies, order values, and spatial coordinates in Nanded.
- `population.csv`: Synthetic population density and demographic estimates across Nanded localities.
- `roads.csv`: Synthetic road connectivity and accessibility ratings for major Nanded corridors.
- `delivery_centers.csv`: Existing delivery hub locations and operational capacities.
- `locations.csv`: Landmark reference points and commercial nodes across Nanded.
- `auth.sqlite3`: Local SQLite database for user authentication and session management.

---

## 4. Repository Structure
```
smartdeliver-ai/
├── backend/
│   └── app/
│       ├── main.py                     # FastAPI application & API endpoints
│       └── ml/
│           ├── cleaner.py              # Data cleaning and validation pipeline
│           ├── demand.py               # Customer demand aggregation
│           ├── clustering.py           # K-Means, Elbow/WCSS, & Silhouette analysis
│           ├── distance.py             # Haversine distance & coverage calculation
│           ├── candidate_generator.py  # Centroid & candidate location generator
│           ├── scoring.py              # Multi-criteria weighted recommendation scoring
│           ├── explanation.py          # AI recommendation rationale generation
│           └── pipeline.py             # Orchestrates the end-to-end analysis
├── data/
│   ├── auth.sqlite3                    # SQLite authentication database
│   ├── customers_orders.csv            # Synthetic customer order data
│   ├── delivery_centers.csv            # Existing delivery hubs
│   ├── locations.csv                   # Area landmarks
│   ├── population.csv                  # Locality population metrics
│   └── roads.csv                       # Road network metrics
├── frontend/
│   ├── index.html                      # Single-page dashboard application
│   ├── styles.css                      # Application styling
│   └── app.js                          # Vanilla JavaScript frontend controller
├── requirements.txt                    # Python backend dependencies
├── generate_nanded_data.py             # Synthetic data generator script
└── test_backend.py                     # Direct pipeline verification script
```

---

## 5. Decision-Support Features & Multi-Criteria Priorities
The recommendation engine evaluates candidate locations using weighted multi-criteria scoring:
- **Balanced**: Standard default weighting balancing demand, distance, connectivity, cost, and coverage.
- **Fast Delivery**: Prioritizes minimum delivery distance to customer clusters.
- **Low Cost**: Prioritizes lower monthly hub operating expenses.
- **Maximum Customer Coverage**: Emphasizes 5km radius customer reach.
- **High Demand**: Prioritizes high customer order volume clusters.

*(Note: Advanced charts, PDF reports, heatmaps, and dynamic scenario comparisons are planned for later phases and are not yet implemented.)*

---

## 6. How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Application
From the project root:
```bash
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
or run `main.py` directly:
```bash
python backend/app/main.py
```

### 3. Access Dashboard
Open your browser and navigate to:
```
http://127.0.0.1:8000
```
FastAPI automatically serves the vanilla frontend directly at the root URL.

### 4. Run Backend Tests
To verify the ML pipeline and recommendations directly:
```bash
python test_backend.py
```
