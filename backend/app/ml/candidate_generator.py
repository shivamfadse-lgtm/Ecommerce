import pandas as pd
import numpy as np
from app.ml.distance import calculate_distance_metrics, haversine_distance

def generate_candidate_locations(df_clustered: pd.DataFrame, cluster_summaries: list, df_locations: pd.DataFrame, df_roads: pd.DataFrame, df_centers: pd.DataFrame):
    """
    Synthesizes candidate delivery center locations based on:
    1. High-demand cluster centroids
    2. Strategic commercial locations in Nanded
    3. Road network connectivity nodes
    Calculates exact geographic distance metrics to all customer coordinates.
    """
    unique_customers = df_clustered[['customer_id', 'latitude', 'longitude']].drop_duplicates(subset=['customer_id']) if 'customer_id' in df_clustered.columns else df_clustered[['latitude', 'longitude']].drop_duplicates()
    customer_coords = list(zip(unique_customers['latitude'], unique_customers['longitude'])) if not unique_customers.empty else []
    existing_center_coords = list(zip(df_centers['latitude'], df_centers['longitude'])) if not df_centers.empty else []

    candidates = []
    cand_id_counter = 1

    # Strategy 1: Add Candidate for each Cluster Centroid
    for c in cluster_summaries:
        c_lat = c['centroid_latitude']
        c_lng = c['centroid_longitude']
        
        # Calculate real customer distance metrics
        dist_metrics = calculate_distance_metrics(c_lat, c_lng, customer_coords)
        
        # Calculate distance to nearest existing delivery center
        if existing_center_coords:
            min_center_dist = min(haversine_distance(c_lat, c_lng, center[0], center[1]) for center in existing_center_coords)
        else:
            min_center_dist = 5.0

        # Match nearest road for connectivity & traffic score
        road_connectivity = 85
        traffic_score = 45
        highway_dist = 1.0
        if not df_roads.empty:
            road_dists = [haversine_distance(c_lat, c_lng, r['latitude'], r['longitude']) for _, r in df_roads.iterrows()]
            nearest_idx = int(np.argmin(road_dists))
            nearest_road = df_roads.iloc[nearest_idx]
            road_connectivity = int(nearest_road['road_connectivity_score'])
            traffic_score = int(nearest_road['traffic_score'])
            highway_dist = float(nearest_road['highway_distance_km'])

        # Estimated monthly operating cost based on proximity to city center
        base_cost = 125000 + int(c['demand_pct'] * 1200)

        candidates.append({
            "candidate_id": f"CAND{cand_id_counter:02d}",
            "area": f"Centroid Hub - {c['label']} ({c['cluster_name']})",
            "latitude": round(c_lat, 6),
            "longitude": round(c_lng, 6),
            "customer_demand": int(c['total_order_value']),
            "orders": int(c['order_count']),
            "average_delivery_distance": dist_metrics["avg_distance_km"],
            "median_delivery_distance": dist_metrics["median_distance_km"],
            "max_delivery_distance": dist_metrics["max_distance_km"],
            "road_connectivity": road_connectivity,
            "traffic_score": traffic_score,
            "operating_cost": base_cost,
            "highway_distance": round(highway_dist, 2),
            "existing_center_distance": round(min_center_dist, 2),
            "coverage_percentage": dist_metrics["within_5km_pct"],
            "within_2km_pct": dist_metrics["within_2km_pct"],
            "within_10km_pct": dist_metrics["within_10km_pct"],
            "source_type": "Cluster Centroid"
        })
        cand_id_counter += 1

    # Strategy 2: Add Candidate for Predefined Strategic Locations
    if not df_locations.empty:
        for _, loc in df_locations.iterrows():
            loc_lat = float(loc['latitude'])
            loc_lng = float(loc['longitude'])
            
            dist_metrics = calculate_distance_metrics(loc_lat, loc_lng, customer_coords)
            
            if existing_center_coords:
                min_center_dist = min(haversine_distance(loc_lat, loc_lng, center[0], center[1]) for center in existing_center_coords)
            else:
                min_center_dist = 5.0

            # Match nearest road
            road_connectivity = 80
            traffic_score = 50
            if not df_roads.empty:
                road_dists = [haversine_distance(loc_lat, loc_lng, r['latitude'], r['longitude']) for _, r in df_roads.iterrows()]
                nearest_idx = int(np.argmin(road_dists))
                nearest_road = df_roads.iloc[nearest_idx]
                road_connectivity = int(nearest_road['road_connectivity_score'])
                traffic_score = int(nearest_road['traffic_score'])

            # Keep candidate demand tied to the cleaned order dataset.
            local_mask = df_clustered.apply(
                lambda row: haversine_distance(loc_lat, loc_lng, row['latitude'], row['longitude']) <= 3.0,
                axis=1,
            )
            local_orders = df_clustered[local_mask]
            local_customer_count = int(local_orders['customer_id'].nunique()) if 'customer_id' in local_orders.columns else len(local_orders)
            local_demand = float(local_orders['order_value'].sum()) if 'order_value' in local_orders.columns else 0.0
            local_order_count = int(local_orders['orders_count'].sum()) if 'orders_count' in local_orders.columns else len(local_orders)

            candidates.append({
                "candidate_id": f"CAND{cand_id_counter:02d}",
                "area": str(loc['area']),
                "latitude": round(loc_lat, 6),
                "longitude": round(loc_lng, 6),
                "customer_demand": round(local_demand, 2),
                "customers": local_customer_count,
                "orders": local_order_count,
                "average_delivery_distance": dist_metrics["avg_distance_km"],
                "median_delivery_distance": dist_metrics["median_distance_km"],
                "max_delivery_distance": dist_metrics["max_distance_km"],
                "road_connectivity": road_connectivity,
                "traffic_score": traffic_score,
                "operating_cost": int(loc['operating_cost']),
                "highway_distance": round(float(loc['highway_distance_km']), 2),
                "existing_center_distance": round(min_center_dist, 2),
                "coverage_percentage": dist_metrics["within_5km_pct"],
                "within_2km_pct": dist_metrics["within_2km_pct"],
                "within_10km_pct": dist_metrics["within_10km_pct"],
                "source_type": "Strategic Landmark"
            })
            cand_id_counter += 1

    return candidates
