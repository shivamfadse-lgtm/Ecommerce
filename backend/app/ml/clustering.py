import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from app.ml.distance import haversine_distance

def evaluate_kmeans_elbow_silhouette(df: pd.DataFrame, max_k: int = 8):
    """
    Computes WCSS / Inertia and Silhouette scores for K from 2 to max_k
    using scikit-learn.
    Returns lists for Elbow Chart & Silhouette Chart.
    """
    features = df[['latitude', 'longitude', 'order_value']].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    elbow_data = []
    silhouette_data = []

    best_silhouette = -1.0
    optimal_k_sil = 4  # default fallback

    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        
        inertia = float(kmeans.inertia_)
        elbow_data.append({"k": k, "wcss": round(inertia, 2)})

        sil = float(silhouette_score(X_scaled, labels))
        silhouette_data.append({"k": k, "silhouette_score": round(sil, 4)})

        if sil > best_silhouette:
            best_silhouette = sil
            optimal_k_sil = k

    return elbow_data, silhouette_data, optimal_k_sil

def run_kmeans_clustering(df: pd.DataFrame, k_clusters: int = 4, auto_k: bool = False):
    """
    Executes scikit-learn K-Means clustering on the cleaned dataset.
    Assigns each record to a cluster and calculates exact centroids and stats.
    """
    if df.empty:
        return {}, df

    elbow_data, silhouette_data, optimal_k = evaluate_kmeans_elbow_silhouette(df, max_k=8)

    if auto_k or k_clusters < 2 or k_clusters > 8:
        k_clusters = optimal_k

    features = df[['latitude', 'longitude', 'order_value']].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=k_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)

    df_clustered = df.copy()
    df_clustered['cluster_id'] = cluster_labels

    # Compute unscaled Centroids (average lat & lon of actual cluster members)
    total_val_sum = df_clustered['order_value'].sum()
    
    cluster_summaries = []
    all_cluster_orders = []

    for cid in range(k_clusters):
        c_df = df_clustered[df_clustered['cluster_id'] == cid]
        if c_df.empty:
            continue

        c_cust = int(c_df['customer_id'].nunique()) if 'customer_id' in c_df.columns else len(c_df)
        c_orders = int(c_df['orders_count'].sum()) if 'orders_count' in c_df.columns else len(c_df)
        c_total_val = float(c_df['order_value'].sum())
        c_avg_val = float(c_df['order_value'].mean())
        c_lat = float(c_df['latitude'].mean())
        c_lng = float(c_df['longitude'].mean())
        c_demand_pct = round((c_total_val / max(total_val_sum, 1.0)) * 100, 2)

        # Average distance from members to centroid
        member_coords = list(zip(c_df['latitude'], c_df['longitude']))
        dists = [haversine_distance(c_lat, c_lng, lat, lon) for lat, lon in member_coords]
        c_avg_dist = round(sum(dists) / len(dists), 2) if dists else 0.0

        all_cluster_orders.append(c_orders)

        cluster_summaries.append({
            "cluster_id": cid,
            "cluster_name": f"Cluster #{cid + 1}",
            "customer_count": c_cust,
            "order_count": c_orders,
            "total_order_value": round(c_total_val, 2),
            "avg_order_value": round(c_avg_val, 2),
            "centroid_latitude": round(c_lat, 6),
            "centroid_longitude": round(c_lng, 6),
            "demand_pct": c_demand_pct,
            "avg_member_distance_km": c_avg_dist
        })

    # Dynamically assign labels based on order count percentiles
    if all_cluster_orders:
        max_orders = max(all_cluster_orders)
        min_orders = min(all_cluster_orders)
        range_orders = max_orders - min_orders if max_orders != min_orders else 1.0

        for c in cluster_summaries:
            norm_val = (c['order_count'] - min_orders) / range_orders
            if norm_val >= 0.66:
                c['label'] = "High Demand Zone"
            elif norm_val >= 0.33:
                c['label'] = "Medium Demand Zone"
            else:
                c['label'] = "Low Demand Zone"

    results = {
        "selected_k": k_clusters,
        "optimal_k": optimal_k,
        "elbow_data": elbow_data,
        "silhouette_data": silhouette_data,
        "cluster_summaries": cluster_summaries
    }

    return results, df_clustered
