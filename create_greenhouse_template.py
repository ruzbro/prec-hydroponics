import pandas as pd
import numpy as np
import argparse

def create_greenhouse_template(greenhouse_id):
    gh4_template_path = "/workspaces/prec_hydroponics/data/GH4 Template - data gh4.csv"
    output_path = f"/workspaces/prec_hydroponics/data/{greenhouse_id} Template - data {greenhouse_id.lower()}.csv"

    try:
        # Read the GH4 template
        gh4_template_df = pd.read_csv(gh4_template_path)

        # Select the first three columns
        greenhouse_template_df = gh4_template_df[['metric_code', 'date_time', 'week_num']].copy()

        # Add an empty 'value' column
        greenhouse_template_df['value'] = np.nan

        # Set the 'location' column to the provided greenhouse_id
        greenhouse_template_df['location'] = greenhouse_id

        # Save the new template
        greenhouse_template_df.to_csv(output_path, index=False)
        print(f"Successfully created {greenhouse_id} template at {output_path}")

    except FileNotFoundError as e:
        print(f"Error: Template file not found - {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a greenhouse data template.")
    parser.add_argument('greenhouse_id', type=str, help='The ID of the greenhouse (e.g., GH1, GH2, GH3)')
    args = parser.parse_args()
    create_greenhouse_template(args.greenhouse_id)