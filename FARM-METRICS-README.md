# Farm Metrics Data Verification and Status

This document outlines the data verification process applied to the merged Hydronomics data (`Hydronomics Data Merged.csv`) and explains the `status` column added to the dataset.

## Purpose of the `status` Column

The `status` column is added to `Hydronomics Data Merged.csv` to flag data points that may require further investigation due to being outside expected ranges or being non-numeric. This helps in identifying potential sensor errors, data entry mistakes, or unusual but possibly valid readings.

## Status Codes and Definitions

Each row in the `Hydronomics Data Merged.csv` file now has a `status` indicating the result of the initial data verification. The possible status codes are:

*   **`NULL` (Normal)**: The data point's `value` falls within the predefined expected range for its `metric_code`. This is the expected status for the vast majority of data.
*   **`out-of-range`**: The data point's `value` is outside the physically possible or highly improbable range for its `metric_code`. These values are strong indicators of errors.
*   **`low-ec-to-verify`**: This status is specific to Electrical Conductivity (EC) metrics (`sys_ec` and `fwater_ec`). It indicates that the EC `value` is less than 1000. While not necessarily an error (e.g., for freshwater), it's flagged for verification as typical nutrient solutions often have EC values above 1000. This helps distinguish between genuinely low EC and potential issues.
*   **`non-numeric`**: The `value` for the `metric_code` was not a valid number and could not be converted to a numeric type. These entries were coerced to `NaN` during processing.

## Defined Ranges for Metrics

The following ranges are used to determine the `normal` and `out-of-range` statuses. Values outside these ranges (excluding `low-ec-to-verify` for EC) are marked as `out-of-range`.

| Metric Code        | Metric Name                  | Minimum Expected Value | Maximum Expected Value | Special Notes                                                              |
| :----------------- | :--------------------------- | :--------------------- | :--------------------- | :------------------------------------------------------------------------- |
| `sys_ec`           | System EC                    | 0                      | 10000                  | Values < 1000 are flagged as `low-ec-to-verify` for further inspection.    |
| `fwater_ec`        | Freshwater EC                | 0                      | 10000                  | Values < 1000 are flagged as `low-ec-to-verify` for further inspection.    |
| `sys_ph`           | System PH                    | 0                      | 14                     |                                                                            |
| `fwater_ph`        | Freshwater PH                | 0                      | 14                     |                                                                            |
| `sys_h20_temp`     | Water Temp                   | -20                    | 60                     | Temperatures are in Celsius.                                               |
| `fwater_temp`      | Freshwater Temp              | -20                    | 60                     | Temperatures are in Celsius.                                               |
| `sys_gh_temp`      | Greenhouse Temp              | -20                    | 60                     | Temperatures are in Celsius.                                               |
| `sys_gh_rh`        | Greenhouse Relative Humidity | 0                      | 100                    | Values are percentages.                                                    |

## How to Use This Information

Users can filter the `Hydronomics Data Merged.csv` file by the `status` column to quickly identify data points that need attention. For example, filtering for `out-of-range` values will show critical errors, while `low-ec-to-verify` will highlight data that might be unusual but requires expert judgment.

## Macro-Level Farm Metrics Analysis

The `macro-farm-metrics-analysis.py` script provides a high-level analysis of temperature metrics across different greenhouses.

### Features

*   **Analyzes Clean Data**: The script uses only clean data from `Hydronomics Data Merged.csv` (where `status` is `NULL`).
*   **Weekly Median Calculation**: It calculates the median weekly value for each temperature metric by greenhouse.
*   **Identifies Extremes**: The script identifies which greenhouse had the highest and lowest median temperature values for each metric.
*   **Pattern Analysis**: It analyzes and reports on consistent temperature differences between greenhouses.

### How to Run the Analysis in IPython

You can run the analysis in an IPython interactive session.

1.  **Start IPython**:
    ```bash
    ipython
    ```

2.  **Import the function**:
    ```python
    from macro_farm_metrics_analysis import analyze_temperature_patterns
    ```

3.  **Run the analysis**:
    *   To run the analysis for all greenhouses and all temperature metrics:
        ```python
        analyze_temperature_patterns()
        ```
    *   To run the analysis for specific greenhouses and metrics:
        ```python
        analyze_temperature_patterns(target_greenhouses=['GH1', 'GH3'], target_metrics=['sys_gh_temp'])
        ```
