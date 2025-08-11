import pandas as pd
import numpy as np
import os

data_dir = '/workspaces/prec_hydroponics/data'
merged_file = os.path.join(data_dir, 'Hydronomics Data Merged.csv')

# Define ranges for each metric
METRIC_RANGES = {
    'sys_ec': {'min': 0, 'max': 10000, 'low_threshold': 1000},
    'fwater_ec': {'min': 0, 'max': 10000, 'low_threshold': 1000},
    'sys_ph': {'min': 0, 'max': 14},
    'fwater_ph': {'min': 0, 'max': 14},
    'sys_h20_temp': {'min': -20, 'max': 60},
    'fwater_temp': {'min': -20, 'max': 60},
    'sys_gh_temp': {'min': -20, 'max': 60},
    'sys_gh_rh': {'min': 0, 'max': 100}
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

# Set default status to NaN (NULL in CSV)
df['status'] = np.nan

# Convert 'value' column to numeric, coercing errors to NaN
df['value'] = pd.to_numeric(df['value'], errors='coerce')

# Apply status logic
for index, row in df.iterrows():
    metric_code = row['metric_code']
    value = row['value']

    if pd.isna(value):
        df.at[index, 'status'] = 'non-numeric'
        continue

    if metric_code in METRIC_RANGES:
        ranges = METRIC_RANGES[metric_code]
        
        # Check for out-of-range values
        if value < ranges['min'] or value > ranges['max']:
            df.at[index, 'status'] = 'out-of-range'
        
        # Specific check for EC values less than low_threshold
        elif 'ec' in metric_code and value < ranges['low_threshold']:
            df.at[index, 'status'] = 'low-ec-to-verify'

# Save the updated DataFrame back to CSV
try:
    df.to_csv(merged_file, index=False)
    print(f"Successfully updated {merged_file} with 'status' column.")
except Exception as e:
    print(f"Error saving updated file: {e}")
