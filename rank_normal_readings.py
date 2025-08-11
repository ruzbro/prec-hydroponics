import pandas as pd
import numpy as np
import os

data_dir = '/workspaces/prec_hydroponics/data'
merged_file = os.path.join(data_dir, 'Agrometrics Data Merged.csv')

try:
    df = pd.read_csv(merged_file)
    print(f"Successfully loaded {merged_file}\n")
except FileNotFoundError:
    print(f"Error: Merged file not found at {merged_file}")
    exit()
except Exception as e:
    print(f"Error loading merged file: {e}")
    exit()

print("--- Percentage of Normal Readings per Metric ---")

# Calculate total readings per metric
total_readings_per_metric = df.groupby('metric_code').size().reset_index(name='total_readings')

# Calculate normal readings per metric (where status is NaN)
normal_readings_per_metric = df[df['status'].isna()].groupby('metric_code').size().reset_index(name='normal_readings')

# Merge the two dataframes
merged_counts = pd.merge(total_readings_per_metric, normal_readings_per_metric, on='metric_code', how='left')

# Fill NaN normal_readings with 0 (for metrics that have no normal readings)
merged_counts['normal_readings'] = merged_counts['normal_readings'].fillna(0).astype(int)

# Calculate percentage of normal readings
merged_counts['percentage_normal'] = (merged_counts['normal_readings'] / merged_counts['total_readings']) * 100

# Rank from highest to lowest percentage
ranked_metrics = merged_counts.sort_values(by='percentage_normal', ascending=False)

# Display the results
print(ranked_metrics.to_string(index=False))

print("\n--- End of Report ---")
