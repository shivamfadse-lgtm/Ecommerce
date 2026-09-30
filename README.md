# SMARTDELIVER AI — E-Commerce Delivery Center Location Optimization

> **Full Project Title**: AI-Based E-Commerce Delivery Center Location Optimization Using Geospatial Data and K-Means Clustering  
> **Primary Target City**: Nanded, Maharashtra, India (~19.1550° N, 77.3100° E)

---

## 1. Project Overview & Business Purpose
**SMARTDELIVER AI** is an enterprise-grade B2B logistics intelligence platform designed to answer a fundamental business question for e-commerce companies:

> **"Where should an e-commerce company open its next delivery center in a city?"**

The platform evaluates spatial customer demand patterns, applies scikit-learn K-Means clustering, computes WCSS (Inertia) for the Elbow Method and Silhouette scores, synthesizes candidate delivery center sites from cluster centroids and road network nodes, and scores each site using a multi-criteria decision-support engine.

---

## 2. Research Methodology & Data Pipeline
Adapted from geospatial AI methodologies:
1. **Data Collection**: Spatial customer & order locations, road network connectivity, traffic levels, operating costs, existing delivery hubs.
2. **Data Cleaning**: Pandas validation pipeline filtering missing values, duplicates, and out-of-bounds coordinates with summary metrics.
3. **Exploratory Data Analysis**: Demand aggregation, orders by locality, daily demand trends, order value distribution.
4. **K-Means Clustering**: Scikit-learn `KMeans` fitting across $K=2..8$ on standardized spatial features.
5. **Elbow Method & WCSS**: WCSS calculation across $K=2..8$ for curvature evaluation.
6. **Silhouette Analysis**: Evaluation of cluster separation efficiency to determine optimal $K$.
7. **Cluster Centroids**: Computation of unscaled cluster center coordinates as candidate anchors.
8. **Candidate Site Generation**: Synthesizing 5-11 candidate sites from centroids, commercial nodes, and road junctions.
9. **Geographic Distance**: Haversine distance calculations for average distance, median distance, max distance, and 2km / 5km / 10km catchment coverage.
10. **Multi-Criteria Scoring Engine**:
    $$Final\ Score = 0.30 \times Demand + 0.25 \times Distance + 0.15 \times Connectivity + 0.15 \times Cost + 0.15 \times Coverage$$
    Supports dynamic priority presets (*Fast Delivery*, *Low Cost*, *Maximum Coverage*, *High Demand*, *Balanced*).
11. **Dynamic AI Rationale**: Automated generation of positive strengths and risk considerations.
12. **Map Visualization**: Interactive OpenStreetMap centered on Nanded with custom layer toggles.

---

## 3. Nanded Public Data Research Inventory
1. **Nanded Ward Boundaries**: NWCMC Portal ([nwcmc.gov.in](https://www.nwcmc.gov.in)) & Datameet India Maps (GeoJSON/Shapefile).
2. **Census Population & Households**: Census of India 2011 Primary Census Abstract via [data.gov.in](https://data.gov.in) (550,439 population, 102,297 households).
3. **Geographic Coordinates**: OpenStreetMap Overpass Turbo / Nominatim API for Nanded localities (Anand Nagar, Taroda Naka, CIDCO, Workshop Corner, Old Nanded, Vasmat Road, Vishnupuri).
4. **Road Network**: OpenStreetMap Geofabrik India extract (NH-61, Hingoli Rd, Airport Rd, CIDCO Expressway, Vasmat Rd Bypass).
5. **Shops & Commercial POIs**: OpenStreetMap POI data.
6. **Demographics & Income**: Maharashtra DES District Statistical Abstract.
7. **Customer Order Data**: Real e-commerce customer coordinates are proprietary private commercial data. Generated a clearly labeled simulated dataset: `nanded_customer_data.csv` (`customer_id, latitude, longitude, orders, ward`).

---

## 4. Project Structure
```
smartdeliver-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entry point & CORS
│   │   ├── config.py                   # System configuration
│   │   ├── database/
│   │   │   ├── session.py              # SQLite / SQLAlchemy connection
│   │   │   └── models.py               # Database ORM models
│   │   ├── schemas/
│   │   │   └── schemas.py              # Pydantic data schemas
│   │   ├── ml/
│   │   │   ├── cleaner.py              # Pandas data cleaning module
│   │   │   ├── demand.py               # Demand metrics & aggregations
│   │   │   ├── clustering.py           # K-Means, Elbow & Silhouette Analysis
│   │   │   ├── distance.py             # Haversine distance calculator
│   │   │   ├── candidate_generator.py  # Centroid & candidate synthesizer
│   │   │   ├── scoring.py              # Location scoring engine (0-100)
│   │   │   └── explanation.py          # Dynamic AI rationale generator
│   │   └── routes/                     # REST API routing endpoints
│   │       ├── analyze.py
│   │       ├── demand.py
│   │       ├── kmeans.py
│   │       ├── candidates.py
│   │       ├── centers.py
│   │       └── upload.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/                 # Sidebar, Header, Layout
│   │   │   ├── map/                    # Leaflet Map with custom layers
│   │   │   └── ui/                     # LocationDetailDrawer, badges
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── BusinessRequirements.jsx
│   │   │   ├── CustomerDemand.jsx
│   │   │   ├── Recommendations.jsx
│   │   │   ├── LocationComparison.jsx
│   │   │   ├── MapViewPage.jsx
│   │   │   ├── AIAnalytics.jsx
│   │   │   ├── ClusterExplorer.jsx
│   │   │   ├── ExistingCenters.jsx
│   │   │   ├── DataUpload.jsx
│   │   │   └── Settings.jsx
│   │   ├── services/
│   │   │   └── api.js                  # Axios API client
│   │   ├── App.jsx                     # Router & state management
│   │   └── index.css                   # Tailwind CSS styling
│   └── package.json
└── data/
    ├── customers_orders.csv            # 1,000 Nanded order records
    ├── nanded_customer_data.csv        # Simulated customer order dataset
    ├── roads.csv                       # Nanded road network data
    ├── delivery_centers.csv            # Existing Nanded delivery hubs
    └── locations.csv                   # Predefined Nanded area landmarks
```

---

## 5. API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/analyze` | Runs complete end-to-end Nanded optimization pipeline |
| `GET` | `/api/demand` | Returns customer demand metrics & area summary |
| `GET` | `/api/customers` | Returns sample cleaned customer records |
| `GET` | `/api/clusters` | Returns K-Means cluster summaries, Elbow curve & Silhouette scores |
| `GET` | `/api/candidates` | Returns candidate sites scored according to active priority |
| `GET` | `/api/recommendations` | Returns #1 AI recommended delivery center & rationale |
| `GET` | `/api/existing-centers` | Returns current delivery hub utilization levels |
| `POST` | `/api/upload` | Uploads CSV dataset, validates schema, updates pipeline |
| `POST` | `/api/compare` | Compares 2-3 candidate locations side-by-side |

---

## 6. How to Run

### Backend Startup
```bash
cd smartdeliver-ai/backend
py app/main.py
```
*FastAPI server runs on `http://127.0.0.1:8000`.*

### Frontend Startup
```bash
cd smartdeliver-ai/frontend
cmd /c "npm run dev"
```
*Vite dev server runs on `http://localhost:5173`.*
