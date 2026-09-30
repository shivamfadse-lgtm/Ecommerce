from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd

from app.ml.candidate_generator import generate_candidate_locations
from app.ml.cleaner import clean_customer_data
from app.ml.clustering import run_kmeans_clustering
from app.ml.demand import calculate_customer_demand
from app.ml.scoring import explain_candidate, score_candidates


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


class AnalysisPipeline:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.payload: dict[str, Any] = {}

    def run(self, priority: str = "Balanced", k: int = 4, orders: pd.DataFrame | None = None) -> dict[str, Any]:
        raw = orders if orders is not None else pd.read_csv(self.data_dir / "customers_orders.csv")
        clean, quality = clean_customer_data(raw)
        clustering, clustered = run_kmeans_clustering(clean, k_clusters=k, auto_k=k < 2)
        demand = calculate_customer_demand(clean)
        population = pd.read_csv(self.data_dir / "population.csv")
        population_by_area = (
            population.groupby("area", as_index=False)
            .agg(
                population=("person_id", "count"),
                average_age=("age", "mean"),
                online_shoppers=("is_online_shopper", "sum"),
                average_household_size=("household_size", "mean"),
            )
            .assign(
                average_age=lambda frame: frame["average_age"].round(1),
                online_shopper_pct=lambda frame: (frame["online_shoppers"] / frame["population"] * 100).round(1),
                average_household_size=lambda frame: frame["average_household_size"].round(1),
            )
            .to_dict(orient="records")
        )
        age_bands = pd.cut(
            population["age"],
            bins=[0, 17, 29, 44, 59, 200],
            labels=["0-17", "18-29", "30-44", "45-59", "60+"],
        ).value_counts().sort_index()
        gender_summary = population["gender"].value_counts().to_dict()
        locations = pd.read_csv(self.data_dir / "locations.csv")
        roads = pd.read_csv(self.data_dir / "roads.csv")
        centers = pd.read_csv(self.data_dir / "delivery_centers.csv")
        candidates = generate_candidate_locations(clustered, clustering["cluster_summaries"], locations, roads, centers)
        ranked, weights = score_candidates(candidates, priority)
        recommendation = ranked[0] if ranked else None
        explanation = explain_candidate(recommendation, centers.to_dict(orient="records")) if recommendation else {"summary": "No recommendation available.", "positive_factors": [], "risks": []}
        center_records = centers.to_dict(orient="records")
        for center in center_records:
            center["utilization"] = round(center["current_daily_orders"] / max(center["capacity_per_day"], 1) * 100, 1)
        customer_records = clustered[["order_id", "customer_id", "latitude", "longitude", "area", "order_value", "orders_count", "cluster_id"]].to_dict(orient="records")
        self.payload = {
            "city": "Nanded",
            "state": "Maharashtra",
            "demo_mode": True,
            "quality": quality,
            "population": {
                "total_people": int(len(population)),
                "area_summary": population_by_area,
                "age_bands": [{"band": str(band), "people": int(count)} for band, count in age_bands.items()],
                "gender_summary": {str(key): int(value) for key, value in gender_summary.items()},
                "online_shoppers": int(population["is_online_shopper"].sum()),
                "online_shopper_pct": round(float(population["is_online_shopper"].mean() * 100), 1),
                "average_household_size": round(float(population["household_size"].mean()), 1),
                "source": "synthetic Nanded population dataset",
            },
            "demand": demand,
            "analytics": {"optimal_k": clustering["optimal_k"], "selected_k": clustering["selected_k"], "elbow": clustering["elbow_data"], "silhouette": clustering["silhouette_data"]},
            "clusters": clustering["cluster_summaries"],
            "candidates": ranked,
            "recommendation": recommendation,
            "explanation": explanation,
            "weights": weights,
            "existing_centers": center_records,
            "customers": customer_records,
        }
        self.payload = _json_safe(self.payload)
        return self.payload
