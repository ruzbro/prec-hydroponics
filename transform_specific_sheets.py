import pandas as pd
import numpy as np
import re

def transform_specific_sheet(xls_path, sheet_name, output_filename):
    print(f"Processing sheet: {sheet_name}")
    
    # Extract location from sheet name
    location_match = re.search(r'(GH[1-4]|NURSERY)', sheet_name, re.IGNORECASE)
    if not location_match:
        print(f"Could not extract location from sheet name: {sheet_name}")
        return
    location = location_match.group(1).upper()

    # Read the sheet without a header, so we can manually select rows/columns
    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    # Week numbers are in row 3 (index 3), starting from column 2 (index 2)
    week_numbers_series = df.iloc[3, 2:]

    # Define the exact row mappings for each metric_code and its starting DAILY data row
    # (metric_code, daily_data_start_row_index_in_pandas)
    metric_daily_data_start_rows = {
        'sys_ec': 20, # Excel row 21 (Mon for EC)
        'sys_ph': 28, # Excel row 29 (Mon for PH)
        'sys_h20_temp': 36, # Excel row 37 (Mon for H2O Temp)
        'sys_gh_temp': 44, # Excel row 45 (Mon for GH Temp)
        'sys_gh_rh': 52, # Excel row 53 (Mon for GH RH)
        'fwater_ec': 61, # Excel row 62 (Mon for FWater EC)
        'fwater_ph': 69, # Excel row 70 (Mon for FWater PH)
        'fwater_temp': 77  # Excel row 78 (Mon for FWater Temp)
    }

    tidy_rows = []

    for metric_code, daily_start_row_index in metric_daily_data_start_rows.items():
        # Iterate through the 7 daily readings for each metric
        for day_offset in range(7): # 0 for Monday, 1 for Tuesday, ..., 6 for Sunday
            current_data_row_index = daily_start_row_index + day_offset
            
            # Iterate through week numbers (columns)
            for col_idx, week_num_val in enumerate(week_numbers_series):
                # Ensure week_num_val is a valid number between 1 and 53
                if pd.notna(week_num_val) and isinstance(week_num_val, (int, float)) and 1 <= week_num_val <= 53:
                    # Get the value from the corresponding cell
                    value = df.iloc[current_data_row_index, 2 + col_idx] # 2 + col_idx because data starts from column 2
                    
                    # Preserve NULL values (NaN) - removed the pd.notna(value) check
                    # Calculate the actual date for this specific day of the week
                    # %w: weekday as a decimal number, where 0 is Sunday and 6 is Saturday.
                    # We want 1 for Monday, 2 for Tuesday, ..., 6 for Sat, 0 for Sun.
                    day_of_week_iso = (day_offset + 1) % 7 # 1=Mon, 2=Tue, ..., 6=Sat, 0=Sun
                    
                    # Construct the week string for date parsing
                    week_str = f"2025-{int(week_num_val):02d}-{day_of_week_iso}"
                    
                    try:
                        date_time = pd.to_datetime(week_str, format='%Y-%W-%w')
                    except ValueError:
                        # Fallback for edge cases or if week starts on different day
                        # Get Monday of the week, then add day_offset
                        base_date = pd.to_datetime(f"2025-{int(week_num_val):02d}-1", format='%Y-%W-%w')
                        date_time = base_date + pd.Timedelta(days=day_offset)

                    tidy_rows.append({
                        'metric_code': metric_code,
                        'date_time': date_time,
                        'week_num': f"2025-{int(week_num_val):02d}", # Keep week_num as YYYY-WW
                        'value': value,
                        'location': location
                    })

    if not tidy_rows:
        print(f"No data found to process for sheet: {sheet_name}.")
        # Create an empty CSV with headers if no data is found
        pd.DataFrame(columns=['metric_code', 'date_time', 'week_num', 'value', 'location']).to_csv(output_filename, index=False)
        return

    result_df = pd.DataFrame(tidy_rows)
    result_df = result_df.sort_values(by=['metric_code', 'date_time']).reset_index(drop=True)

    # Select and reorder final columns
    result_df = result_df[['metric_code', 'date_time', 'week_num', 'value', 'location']]

    result_df.to_csv(output_filename, index=False)
    print(f"Successfully transformed {sheet_name} and saved to {output_filename}")

# --- Main execution block ---
xls_file_path = "/workspaces/prec_hydroponics/data/HGI Agrometrics 2025-07-26.xlsx"

# Process GH2, GH4, and Nursery sheets
transform_specific_sheet(xls_file_path, 'Hydronomics GH2', '/workspaces/prec_hydroponics/data/Hydronomics Data gh2.csv')
transform_specific_sheet(xls_file_path, 'Hydronomics GH4', '/workspaces/prec_hydroponics/data/Hydronomics Data gh4.csv')
transform_specific_sheet(xls_file_path, 'Hydronomics NURSERY', '/workspaces/prec_hydroponics/data/Hydronomics Data nursery.csv')