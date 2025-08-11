import pandas as pd
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

print("--- Querying pH Values Less Than 1000 ---")

# Filter for sys_ph and fwater_ph metrics
ph_df = df[df['metric_code'].isin(['sys_ph', 'fwater_ph'])].copy()

# Convert 'value' column to numeric, coercing errors to NaN
ph_df['value'] = pd.to_numeric(ph_df['value'], errors='coerce')

# Drop rows where 'value' became NaN after conversion (non-numeric entries)
ph_df.dropna(subset=['value'], inplace=True)

# Filter for values less than 1000
filtered_ph_values = ph_df[ph_df['value'] < 1000]

if filtered_ph_values.empty:
    print("No pH values less than 1000 found.")
else:
    print(f"Found {len(filtered_ph_values)} pH values less than 1000.\n")
    # Sort by metric_code and then by value for better readability
    filtered_ph_values_sorted = filtered_ph_values.sort_values(by=['metric_code', 'value'])
    print(filtered_ph_values_sorted.to_string(index=False))

print("\n--- End of Query Report ---")

