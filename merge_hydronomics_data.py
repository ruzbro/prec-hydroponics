import pandas as pd
import os

data_dir = '/workspaces/prec_hydroponics/data'
output_file = os.path.join(data_dir, 'Hydronomics Data Merged.csv')

file_names = [
    'Hydronomics Data gh1.csv',
    'Hydronomics Data gh2.csv',
    'Hydronomics Data gh3.csv',
    'Hydronomics Data gh4.csv',
    'Hydronomics Data nursery.csv'
]

all_data = []

for file_name in file_names:
    file_path = os.path.join(data_dir, file_name)
    try:
        df = pd.read_csv(file_path)
        all_data.append(df)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"Error reading {file_name}: {e}")

if all_data:
    merged_df = pd.concat(all_data, ignore_index=True)
    merged_df.to_csv(output_file, index=False)
    print(f"Successfully merged data into {output_file}")
else:
    print("No data to merge. Please check file paths and contents.")
