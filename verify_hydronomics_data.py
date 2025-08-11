import pandas as pd
import numpy as np
import os

data_dir = '/workspaces/prec_hydroponics/data'
merged_file = os.path.join(data_dir, 'Hydronomics Data Merged.csv')

metrics_to_verify = {
    'sys_ec': 'System EC',
    'sys_ph': 'System PH',
    'sys_h20_temp': 'Water Temp',
    'sys_gh_temp': 'Greenhouse Temp',
    'sys_gh_rh': 'Greenhouse Relative Humidity',
    'fwater_ec': 'Freshwater EC',
    'fwater_ph': 'Freshwater PH',
    'fwater_temp': 'Freshwater Temp'
}

try:
    df = pd.read_csv(merged_file)
    print(f"Successfully loaded {merged_file}\n")
except FileNotFoundError:
    print(f"Error: Merged file not found at {merged_file}")
    exit()
except Exception as e:
    print(f"Error loading merged file: {e}")
    exit()

print("--- Anomalous Data Report ---")

anomalies = []

for metric_code, metric_name in metrics_to_verify.items():
    # Filter DataFrame for the current metric_code
    metric_df = df[df['metric_code'] == metric_code].copy()

    if metric_df.empty:
        # print(f"  No data found for metric_code '{metric_code}'.") # Suppress this for cleaner report
        continue

    # Check for non-numeric values in the 'value' column and convert to numeric, coercing errors
    metric_df['value'] = pd.to_numeric(metric_df['value'], errors='coerce')
    
    # Drop NaNs for analysis
    clean_metric_df = metric_df.dropna(subset=['value'])

    if clean_metric_df.empty:
        continue

    # Identify anomalies based on metric type
    outliers = pd.DataFrame()
    if 'ec' in metric_code:
        outliers = clean_metric_df[(clean_metric_df['value'] < 0) | (clean_metric_df['value'] > 10000)]
    elif 'ph' in metric_code:
        outliers = clean_metric_df[(clean_metric_df['value'] < 0) | (clean_metric_df['value'] > 14)]
    elif 'temp' in metric_code:
        outliers = clean_metric_df[(clean_metric_df['value'] < -20) | (clean_metric_df['value'] > 60)]
    elif 'rh' in metric_code:
        outliers = clean_metric_df[(clean_metric_df['value'] < 0) | (clean_metric_df['value'] > 100)]

    if not outliers.empty:
        for _, row in outliers.iterrows():
            anomalies.append({
                'metric_code': metric_code,
                'metric_name': metric_name,
                'location': row['location'],
                'date_time': row['date_time'],
                'value': row['value']
            })

if not anomalies:
    print("No significant anomalies found based on defined ranges.")
else:
    anomalies_df = pd.DataFrame(anomalies)
    
    # Group by location and then by metric_code
    grouped_anomalies = anomalies_df.groupby(['location', 'metric_name', 'metric_code'])

    for (location, metric_name, metric_code), group in grouped_anomalies:
        print(f"\nGreenhouse: {location}")
        print(f"  Metric: {metric_name} ({metric_code})")
        print("    Anomalous Entries:")
        for _, row in group.iterrows():
            print(f"      Date/Time: {row['date_time']}, Value: {row['value']}")

print("\n--- End of Report ---")
