import pandas as pd
import numpy as np
import os

data_dir = '/workspaces/prec_hydroponics/data'
merged_file = os.path.join(data_dir, 'Hydronomics Data Merged.csv')

try:
    df = pd.read_csv(merged_file)
    print(f"Successfully loaded {merged_file}\n")
except FileNotFoundError:
    print(f"Error: Merged file not found at {merged_file}")
    exit()
except Exception as e:
    print(f"Error loading merged file: {e}")
    exit()

# --- Anomaly Analysis ---
print("--- Anomaly Analysis ---")

anomalous_data = df[df['status'].notna()]

if anomalous_data.empty:
    print("No anomalous data found.")
else:
    print("Total Anomalies by Status Type:")
    print(anomalous_data['status'].value_counts())
    print("\n")

    # Group by metric_code and status
    anomalies_by_metric_status = anomalous_data.groupby(['metric_code', 'status']).size().unstack(fill_value=0)
    print("Anomalies by Metric and Status Type:")
    print(anomalies_by_metric_status)
    print("\n")

    # Group by location and status
    anomalies_by_location_status = anomalous_data.groupby(['location', 'status']).size().unstack(fill_value=0)
    print("Anomalies by Greenhouse (Location) and Status Type:")
    print(anomalies_by_location_status)
    print("\n")

    # Metric with most out-of-range anomalies
    out_of_range_metrics = anomalous_data[anomalous_data['status'] == 'out-of-range']
    if not out_of_range_metrics.empty:
        most_out_of_range_metric = out_of_range_metrics['metric_code'].value_counts().idxmax()
        count = out_of_range_metrics['metric_code'].value_counts().max()
        print(f"Metric with most 'out-of-range' anomalies: {most_out_of_range_metric} ({count} occurrences)")
    else:
        print("No 'out-of-range' anomalies found.")

    # Greenhouse with most out-of-range anomalies
    if not out_of_range_metrics.empty:
        most_out_of_range_location = out_of_range_metrics['location'].value_counts().idxmax()
        count = out_of_range_metrics['location'].value_counts().max()
        print(f"Greenhouse with most 'out-of-range' anomalies: {most_out_of_range_location} ({count} occurrences)")
    else:
        print("No 'out-of-range' anomalies found by greenhouse.")

    # Metric with most low-ec-to-verify anomalies
    low_ec_metrics = anomalous_data[anomalous_data['status'] == 'low-ec-to-verify']
    if not low_ec_metrics.empty:
        most_low_ec_metric = low_ec_metrics['metric_code'].value_counts().idxmax()
        count = low_ec_metrics['metric_code'].value_counts().max()
        print(f"Metric with most 'low-ec-to-verify' anomalies: {most_low_ec_metric} ({count} occurrences)")
    else:
        print("No 'low-ec-to-verify' anomalies found.")

    # Greenhouse with most low-ec-to-verify anomalies
    if not low_ec_metrics.empty:
        most_low_ec_location = low_ec_metrics['location'].value_counts().idxmax()
        count = low_ec_metrics['location'].value_counts().max()
        print(f"Greenhouse with most 'low-ec-to-verify' anomalies: {most_low_ec_location} ({count} occurrences)")
    else:
        print("No 'low-ec-to-verify' anomalies found by greenhouse.")

print("\n--- Completeness Analysis (Missing Values) ---")

# Convert 'value' column to numeric, coercing errors to NaN for missing value analysis
df['value'] = pd.to_numeric(df['value'], errors='coerce')

# Greenhouse with the least amount of null values
null_counts_by_location = df.groupby('location')['value'].apply(lambda x: x.isnull().sum())
if not null_counts_by_location.empty:
    least_null_location = null_counts_by_location.idxmin()
    least_null_count = null_counts_by_location.min()
    print(f"Greenhouse with the least missing values: {least_null_location} ({least_null_count} missing values)")
else:
    print("No data to analyze for missing values by greenhouse.")

# Metric with the most missing values
null_counts_by_metric = df.groupby('metric_code')['value'].apply(lambda x: x.isnull().sum())
if not null_counts_by_metric.empty:
    most_null_metric = null_counts_by_metric.idxmax()
    most_null_count = null_counts_by_metric.max()
    print(f"Metric with the most missing values: {most_null_metric} ({most_null_count} missing values)")
else:
    print("No data to analyze for missing values by metric.")

# Day of the week with the most missing values
df['date_time'] = pd.to_datetime(df['date_time'])
df['day_of_week'] = df['date_time'].dt.day_name()

null_counts_by_day_of_week = df.groupby('day_of_week')['value'].apply(lambda x: x.isnull().sum())
if not null_counts_by_day_of_week.empty:
    most_null_day_of_week = null_counts_by_day_of_week.idxmax()
    most_null_day_count = null_counts_by_day_of_week.max()
    print(f"Day of the week with the most missing values: {most_null_day_of_week} ({most_null_day_count} missing values)")
else:
    print("No data to analyze for missing values by day of week.")

# Combination of metric, greenhouse, and day of the week with the most missing values
null_counts_combined = df.groupby(['metric_code', 'location', 'day_of_week'])['value'].apply(lambda x: x.isnull().sum())
if not null_counts_combined.empty:
    most_null_combined = null_counts_combined.idxmax()
    most_null_combined_count = null_counts_combined.max()
    print(f"Combined (Metric, Greenhouse, Day) with most missing values: {most_null_combined} ({most_null_combined_count} missing values)")
else:
    print("No data to analyze for missing values by combined categories.")

print("\n--- End of Analysis Report ---")
