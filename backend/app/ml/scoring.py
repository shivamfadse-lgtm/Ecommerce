from __future__ import annotations

from typing import Any

import pandas as pd

DEFAULT_WEIGHTS = {
    "demand": 0.30,
    "distance": 0.25,
    "connectivity": 0.15,
    "cost": 0.15,
    "coverage": 0.15,
}

PRIORITY_WEIGHTS = {
    "Balanced": DEFAULT_WEIGHTS,
    "Fast Delivery": {"demand": 0.20, "distance": 0.40, "connectivity": 0.15, "cost": 0.10, "coverage": 0.15},
    "Low Cost": {"demand": 0.20, "distance": 0.15, "connectivity": 0.15, "cost": 0.35, "coverage": 0.15},
    "Maximum Customer Coverage": {"demand": 0.20, "distance": 0.15, "connectivity": 0.10, "cost": 0.10, "coverage": 0.45},
    "High Demand": {"demand": 0.45, "distance": 0.20, "connectivity": 0.15, "cost": 0.10, "coverage": 0.10},
}


def _normalise(values: pd.Series, higher_is_better: bool = True) -> pd.Series:
    low, high = values.min(), values.max()
    if high == low:
        return pd.Series(1.0, index=values.index)
    scaled = (values - low) / (high - low)
    return scaled if higher_is_better else 1 - scaled


def score_candidates(candidates: list[dict[str, Any]], priority: str = "Balanced") -> tuple[list[dict[str, Any]], dict[str, float]]:
    if not candidates:
        return [], PRIORITY_WEIGHTS.get(priority, DEFAULT_WEIGHTS)
    weights = PRIORITY_WEIGHTS.get(priority, DEFAULT_WEIGHTS)
    frame = pd.DataFrame(candidates)
    metrics = {
        "demand_score": _normalise(frame["customer_demand"]),
        "distance_score": _normalise(frame["average_delivery_distance"], False),
        "connectivity_score": _normalise(frame["road_connectivity"]),
        "cost_score": _normalise(frame["operating_cost"], False),
        "coverage_score": _normalise(frame["coverage_percentage"]),
    }
    for key, values in metrics.items():
        frame[key] = (values * 100).round(1)
    frame["ai_score"] = (
        frame["demand_score"] * weights["demand"]
        + frame["distance_score"] * weights["distance"]
        + frame["connectivity_score"] * weights["connectivity"]
        + frame["cost_score"] * weights["cost"]
        + frame["coverage_score"] * weights["coverage"]
    ).round(1)
    frame = frame.sort_values("ai_score", ascending=False).reset_index(drop=True)
    frame["rank"] = frame.index + 1
    ranked = frame.to_dict(orient="records")
    return ranked, weights


def explain_candidate(candidate: dict[str, Any], centers: list[dict[str, Any]]) -> dict[str, list[str] | str]:
    positives = []
    risks = []
    if candidate.get("demand_score", 0) >= 65:
        positives.append("strong customer demand")
    if candidate.get("distance_score", 0) >= 65:
        positives.append("low average delivery distance")
    if candidate.get("connectivity_score", 0) >= 65:
        positives.append("good road connectivity")
    if candidate.get("coverage_score", 0) >= 65:
        positives.append("broad market coverage")
    if candidate.get("cost_score", 0) < 40:
        risks.append("higher operating cost")
    if candidate.get("traffic_score", 0) >= 55:
        risks.append("elevated traffic")
    if candidate.get("highway_distance", 0) > 1.5:
        risks.append("limited highway access")
    if candidate.get("existing_center_distance", 0) < 2:
        risks.append("some overlap with an existing center")
    positive_text = ", ".join(positives) or "a balanced operating profile"
    return {
        "summary": f"AI recommends this location because it offers {positive_text}.",
        "positive_factors": positives,
        "risks": risks,
    }
