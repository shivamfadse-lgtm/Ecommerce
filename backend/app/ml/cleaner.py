import pandas as pd
import numpy as np

def clean_customer_data(df: pd.DataFrame):
    """
    Cleans customer/order dataset using Pandas:
    - Identifies missing lat/long
    - Filters invalid coordinates (e.g. lat outside 18.5 - 20.0, long outside 76.5 - 78.5 for Nanded context)
    - Removes duplicate order rows
    - Handles missing order values or values <= 0
    Returns: cleaned DataFrame and detailed quality diagnostic dictionary.
    """
    total_rows = len(df)
    df = df.copy()

    required_columns = ['order_id', 'customer_id', 'latitude', 'longitude', 'order_date', 'order_value']
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df['order_value'] = pd.to_numeric(df['order_value'], errors='coerce')
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # 1. Check missing values
    missing_lat = df['latitude'].isna().sum() if 'latitude' in df.columns else 0
    missing_lon = df['longitude'].isna().sum() if 'longitude' in df.columns else 0
    missing_order_val = df['order_value'].isna().sum()
    missing_ids = int(df['order_id'].isna().sum() + df['customer_id'].isna().sum())
    missing_dates = int(df['order_date'].isna().sum())
    total_missing = int(missing_lat + missing_lon + missing_order_val + missing_ids + missing_dates)

    # 2. Check duplicates
    duplicates_count = int(df.duplicated(subset=['order_id']).sum()) if 'order_id' in df.columns else int(df.duplicated().sum())

    # Drop duplicates
    if 'order_id' in df.columns:
        df_clean = df.drop_duplicates(subset=['order_id']).copy()
    else:
        df_clean = df.drop_duplicates().copy()

    # 3. Filter missing coordinates & valid coordinate ranges
    df_clean = df_clean.dropna(subset=['order_id', 'customer_id', 'latitude', 'longitude', 'order_date']).copy()
    
    # Valid bounds check for geographic coordinates (-90 <= lat <= 90, -180 <= lon <= 180)
    # and realistic regional filter around Nanded (lat ~ 19.1, lon ~ 77.3)
    valid_coord_mask = (
        (df_clean['latitude'] >= 18.0) & (df_clean['latitude'] <= 20.5) &
        (df_clean['longitude'] >= 76.0) & (df_clean['longitude'] <= 78.5)
    )
    invalid_coords_count = int((~valid_coord_mask).sum())
    df_clean = df_clean[valid_coord_mask].copy()

    # 4. Fill missing numeric values if any
    df_clean['order_value'] = df_clean['order_value'].fillna(df_clean['order_value'].median())
    df_clean = df_clean[df_clean['order_value'] > 0]

    if 'orders_count' in df_clean.columns:
        df_clean['orders_count'] = df_clean['orders_count'].fillna(1).astype(int)

    if 'area' not in df_clean.columns or df_clean['area'].isna().all():
        df_clean['area'] = "Nanded Central"
    else:
        df_clean['area'] = df_clean['area'].fillna("Nanded Suburb")

    final_size = len(df_clean)
    invalid_rows = total_rows - final_size

    quality_summary = {
        "total_rows": int(total_rows),
        "valid_rows": int(final_size),
        "invalid_rows": int(invalid_rows),
        "duplicates_removed": int(duplicates_count),
        "missing_values": int(total_missing),
        "invalid_coordinates_removed": int(invalid_coords_count),
        "final_dataset_size": int(final_size)
    }

    return df_clean, quality_summary
