import pandas as pd
import numpy as np

def calculate_customer_demand(df: pd.DataFrame):
    """
    Computes all key dynamic customer demand metrics from the customer/order dataset.
    No hardcoded values.
    """
    if df.empty:
        return {}

    total_customers = int(df['customer_id'].nunique()) if 'customer_id' in df.columns else len(df)
    total_orders = int(df['orders_count'].sum()) if 'orders_count' in df.columns else len(df)
    total_order_value = float(df['order_value'].sum()) if 'order_value' in df.columns else 0.0
    avg_order_value = float(df['order_value'].mean()) if 'order_value' in df.columns else 0.0
    orders_per_customer = round(total_orders / max(total_customers, 1), 2)

    # Orders by area
    area_summary = []
    if 'area' in df.columns:
        grouped = df.groupby('area').agg(
            customer_count=('customer_id', 'nunique'),
            total_orders=('orders_count', 'sum'),
            total_value=('order_value', 'sum'),
            avg_order_value=('order_value', 'mean'),
            avg_lat=('latitude', 'mean'),
            avg_lng=('longitude', 'mean')
        ).reset_index()

        total_val_sum = grouped['total_value'].sum()
        grouped['demand_pct'] = ((grouped['total_value'] / max(total_val_sum, 1.0)) * 100).round(2)

        # Categorize zones based on demand percentiles
        p75 = grouped['total_orders'].quantile(0.75)
        p25 = grouped['total_orders'].quantile(0.25)

        for _, row in grouped.iterrows():
            if row['total_orders'] >= p75:
                zone_type = "High Demand Zone"
            elif row['total_orders'] >= p25:
                zone_type = "Medium Demand Zone"
            else:
                zone_type = "Low Demand Zone"

            area_summary.append({
                "area": str(row['area']),
                "customer_count": int(row['customer_count']),
                "total_orders": int(row['total_orders']),
                "total_value": round(float(row['total_value']), 2),
                "avg_order_value": round(float(row['avg_order_value']), 2),
                "demand_pct": float(row['demand_pct']),
                "zone_type": zone_type,
                "latitude": round(float(row['avg_lat']), 6),
                "longitude": round(float(row['avg_lng']), 6)
            })

    # Daily demand breakdown if order_date is present
    daily_demand = []
    if 'order_date' in df.columns:
        daily_grp = df.groupby('order_date').agg(
            daily_orders=('orders_count', 'sum'),
            daily_value=('order_value', 'sum')
        ).reset_index().sort_values('order_date')

        for _, row in daily_grp.iterrows():
            daily_demand.append({
                "date": str(row['order_date']),
                "orders": int(row['daily_orders']),
                "revenue": round(float(row['daily_value']), 2)
            })

    # Order value distribution bins
    val_bins = [0, 500, 1000, 2000, 3000, 5000, 10000]
    val_labels = ["<500", "500-1000", "1000-2000", "2000-3000", "3000-5000", "5000+"]
    val_dist = pd.cut(df['order_value'], bins=val_bins, labels=val_labels).value_counts().to_dict()
    order_value_distribution = [{"range": k, "count": int(v)} for k, v in val_dist.items()]

    return {
        "total_customers": total_customers,
        "total_orders": total_orders,
        "total_order_value": round(total_order_value, 2),
        "avg_order_value": round(avg_order_value, 2),
        "orders_per_customer": orders_per_customer,
        "area_summary": area_summary,
        "daily_demand": daily_demand,
        "order_value_distribution": order_value_distribution
    }
