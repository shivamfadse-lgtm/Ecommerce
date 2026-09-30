import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees).
    """
    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def calculate_distance_metrics(candidate_lat: float, candidate_lon: float, customer_coords: list):
    """
    Given candidate location and list of (lat, lon) customer tuples,
    calculate avg, median, max distances and coverage % at thresholds.
    Coverage uses unique customers, and all percent values are capped to 0–100.
    """
    if not customer_coords:
        return {
            "avg_distance_km": 0.0,
            "median_distance_km": 0.0,
            "max_distance_km": 0.0,
            "within_2km_pct": 0.0,
            "within_5km_pct": 0.0,
            "within_10km_pct": 0.0,
            "total_customers": 0
        }

    distances = [haversine_distance(candidate_lat, candidate_lon, c[0], c[1]) for c in customer_coords]
    distances.sort()

    total = len(distances)
    avg_dist = sum(distances) / total
    median_dist = distances[total // 2] if total % 2 != 0 else (distances[total // 2 - 1] + distances[total // 2]) / 2.0
    max_dist = max(distances)

    c_2km = sum(1 for d in distances if d <= 2.0)
    c_5km = sum(1 for d in distances if d <= 5.0)
    c_10km = sum(1 for d in distances if d <= 10.0)

    def pct(num):
        value = (num / total) * 100 if total else 0.0
        return round(max(0.0, min(100.0, value)), 1)

    return {
        "avg_distance_km": round(avg_dist, 2),
        "median_distance_km": round(median_dist, 2),
        "max_distance_km": round(max_dist, 2),
        "within_2km_pct": pct(c_2km),
        "within_5km_pct": pct(c_5km),
        "within_10km_pct": pct(c_10km),
        "total_customers": total
    }
