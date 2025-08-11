import pandas as pd
import numpy as np
import argparse
import re

def populate_greenhouse_template(greenhouse_id):
    # Standardize greenhouse_id for file paths and sheet names
    gh_lower = greenhouse_id.lower()
    
    template_path = f"/workspaces/prec_hydroponics/data/{greenhouse_id} Template - data {gh_lower}.csv"
    excel_path = "/workspaces/prec_hydroponics/data/HGI Agrometrics 2025-07-26.xls" # Hydronomics Monitoring NEW 2025.xlsx"
    
    # Handle sheet name for Nursery specifically, otherwise use Hydronomics GHX
    if greenhouse_id == 'Nursery':
        sheet_name = 'NURSERY'
        output_filename = f"/workspaces/prec_hydroponics/data/Hydronomics Data nursery.csv"
    else:
        sheet_name = f'{greenhouse_id}'
        output_filename = f"/workspaces/prec_hydroponics/data/Hydronomics Data {gh_lower}.csv"

    print(f"Populating template for {sheet_name}...")

    try:
        # Load the template CSV
        template_df = pd.read_csv(template_path)
        
        # Load the Excel sheet without header
        excel_df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)

        # Week numbers are in row 3 (index 3), starting from column 2 (index 2)
        excel_week_numbers_series = excel_df.iloc[3, 2:]
        
        # Create a mapping from week number to Excel column index
        week_to_col_map = {int(week_num): col_idx + 2 for col_idx, week_num in enumerate(excel_week_numbers_series) if pd.notna(week_num) and isinstance(week_num, (int, float))}

        # Define the exact row mappings for each metric_code and its starting DAILY data row
        # This mapping is consistent across GH2, GH3, GH4. Assuming it's the same for GH1 and Nursery.
        metric_daily_data_start_rows = {
            'sys_ec': 20, # Excel row 21 (Mon for EC)
            'sys_ph': 28, # Excel row 29 (Mon for PH)
            'sys_h20_temp': 36, # Excel row 37 (Mon for H2O Temp)
            'sys_gh_temp': 44, # Excel row 45 (Mon for GH Temp)
            'sys_gh_rh': 52, # Excel row 53 (Mon for GH RH)
            'fwater_ec': 62, # Excel row 63 (Mon for FWater EC)
            'fwater_ph': 70, # Excel row 71 (Mon for FWater PH)
            'fwater_temp': 78  # Excel row 79 (Mon for FWater Temp)
        }

        # Iterate through each row of the template DataFrame
        for index, row in template_df.iterrows():
            metric_code = row['metric_code']
            date_time = pd.to_datetime(row['date_time'])
            week_num_str = row['week_num']
            
            # Extract week number (integer) from 'YYYY-WW' format
            week_num_int = int(week_num_str.split('-')[1])

            # Calculate day of the week (0=Monday, 6=Sunday)
            # Pandas weekday is 0=Monday, 6=Sunday. ISO week starts Monday.
            day_of_week_offset = date_time.weekday() # 0 for Mon, 1 for Tue, ..., 6 for Sun

            # Get the starting row index for this metric's daily data block
            daily_data_start_row_index = metric_daily_data_start_rows.get(metric_code)
            if daily_data_start_row_index is None:
                print(f"Warning: Metric code {metric_code} not found in mapping. Skipping row {index}.")
                continue

            # Calculate the exact row in Excel for this specific day's reading
            excel_data_row_index = daily_data_start_row_index + day_of_week_offset

            # Get the Excel column index for this week
            excel_data_col_index = week_to_col_map.get(week_num_int)
            if excel_data_col_index is None:
                # print(f"Warning: Week {week_num_int} not found in Excel columns. Skipping row {index}.")
                template_df.at[index, 'value'] = np.nan # Set value to NaN if week not found
                continue

            # Extract the value from the Excel sheet
            value = excel_df.iloc[excel_data_row_index, excel_data_col_index]
            
            # Populate the 'value' column in the template DataFrame
            template_df.at[index, 'value'] = value

        # Save the updated DataFrame to the output CSV
        template_df.to_csv(output_filename, index=False)
        print(f"Successfully populated {output_filename}")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate a greenhouse data template.")
    parser.add_argument('greenhouse_id', type=str, help='The ID of the greenhouse (e.g., GH1, GH2, GH3, GH4, Nursery)')
    args = parser.parse_args()
    populate_greenhouse_template(args.greenhouse_id)
