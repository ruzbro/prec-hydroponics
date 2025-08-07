# Prompt for Coder AI: MVP Enhancement Plan (Level 1)

## 1. Objective

Upgrade the existing FastAPI application and PostgreSQL database to implement the "Level 1: Responsive Operations and Demand Management" strategy. This involves augmenting the database schema to store more granular farm, crop, and operational data, standardizing data formats, and enhancing the API to support real-time monitoring, unit conversions, and alerts.

## 2. Context

The current MVP is a digital logbook for hydroponic farms. Analysis of existing data (`Hydronomics Data Merged.csv`, `ANALYSIS-BY-CROP-AND-GREENHOUSE.md`, `DATA-INTEGRITY-ANALYSIS.md`) has revealed critical issues, including significant data integrity problems (out-of-range values, missing data) and a lack of crop-specific environmental targets. These shortcomings prevent effective real-time monitoring and lead to operational failures, such as the Arugula crop failure in GH1 due to a critical EC drop.

This plan addresses these issues by building a robust foundation for a climate-resilient application.

## 3. Execution Plan

### 3.1. Database Schema Augmentation (PostgreSQL)

You are to modify the existing Supabase-hosted PostgreSQL database schema. All data should be stored in a single, standard format:
- **Temperature:** Celsius
- **Weight:** Kilograms
- **Volume:** Liters
- **Dates/Timestamps:** ISO 8601

**Apply the following schema changes:**

1.  **`farms` Table:** Add columns to store tenant-specific configurations.
    ```sql
    ALTER TABLE farms
    ADD COLUMN unit_system VARCHAR(20) NOT NULL DEFAULT 'metric', -- e.g., 'metric', 'imperial'
    ADD COLUMN timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',      -- e.g., 'Asia/Singapore'
    ADD COLUMN currency VARCHAR(10) NOT NULL DEFAULT 'USD';       -- e.g., 'USD', 'EUR'
    ```

2.  **`users` Table:** Add a column for language preference.
    ```sql
    ALTER TABLE users
    ADD COLUMN language VARCHAR(10) NOT NULL DEFAULT 'en'; -- e.g., 'en', 'es'
    ```

3.  **`nutrient_profiles` Table:** Create a new table to store nutrient recipes.
    ```sql
    CREATE TABLE nutrient_profiles (
        id SERIAL PRIMARY KEY,
        profile_name VARCHAR(255) NOT NULL UNIQUE,
        target_tds_ppm_min INT,
        target_tds_ppm_max INT,
        nutrient_focus TEXT, -- e.g., 'Growth', 'Fruiting'
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    ```

4.  **`crops` Table:** Augment the table with ideal environmental parameters and link it to `nutrient_profiles`.
    ```sql
    ALTER TABLE crops
    ADD COLUMN ideal_temp_min_celsius NUMERIC(5, 2),
    ADD COLUMN ideal_temp_max_celsius NUMERIC(5, 2),
    ADD COLUMN ideal_light_hours_per_day NUMERIC(4, 2),
    ADD COLUMN nft_suitability_notes TEXT,
    ADD COLUMN nutrient_profile_id INT,
    ADD CONSTRAINT fk_nutrient_profile
        FOREIGN KEY(nutrient_profile_id)
        REFERENCES nutrient_profiles(id);
    ```

5.  **`sensor_readings` Table:** Create a robust table for storing time-series environmental data. This will replace the current CSV-based data logging.
    ```sql
    CREATE TABLE sensor_readings (
        id BIGSERIAL PRIMARY KEY,
        farm_id INT NOT NULL REFERENCES farms(id),
        location_id VARCHAR(50), -- e.g., 'GH1', 'Nursery'
        metric_code VARCHAR(50) NOT NULL, -- e.g., 'sys_ph', 'sys_ec'
        value NUMERIC(10, 2) NOT NULL,
        status VARCHAR(50) DEFAULT 'normal', -- 'normal', 'out_of_range', 'low_ec_to_verify'
        recorded_at TIMESTAMPTZ NOT NULL
    );
    -- Create a hypertable for TimescaleDB if available, for performance
    -- SELECT create_hypertable('sensor_readings', 'recorded_at');
    ```

### 3.2. API Layer Enhancement (FastAPI)

Modify the FastAPI backend to support the new schema and add required business logic.

1.  **Unit Conversion:**
    - Integrate the `Pint` library to handle unit conversions.
    - All data should be converted to the farm's preferred `unit_system` (from the `farms` table) upon request at the API layer. The backend logic and database will continue to operate exclusively in the standard metric units (Celsius, kg, liters).

2.  **Data Ingestion Endpoint:**
    - Create a new endpoint `POST /readings` to accept sensor data.
    - This endpoint must validate incoming data against the predefined ranges in `Farm Metrics Readme.md`.
    - Assign a `status` (`normal`, `out_of_range`, `low_ec_to_verify`, `non-numeric`) to each reading before inserting it into the `sensor_readings` table.

3.  **Monitoring and Alerting Endpoint:**
    - Create an endpoint `GET /farms/{farm_id}/alerts`.
    - This endpoint will compare the latest sensor readings for a given crop/location against the `ideal_temp_min_celsius`, `ideal_temp_max_celsius`, etc., stored in the `crops` table.
    - It should return a list of active alerts for any metric that is outside its defined optimal range.
    - The logic should also monitor for other critical conditions mentioned in the strategy document, such as Dissolved Oxygen (DO) levels below 5 mg/L.

4.  **CRUD Endpoints:**
    - Implement full CRUD (Create, Read, Update, Delete) endpoints for the `farms`, `crops`, and `nutrient_profiles` resources to allow for their management.

## 4. Success Criteria

- The database schema is successfully migrated to the new structure.
- The API can accept, validate, and store sensor readings in the new `sensor_readings` table.
- The API can deliver data converted to the user's preferred unit system.
- The `/alerts` endpoint correctly identifies and reports deviations from the optimal environmental conditions defined in the `crops` table.
- All existing data from `Hydronomics Data Merged.csv` is successfully migrated into the new `sensor_readings` table with correct `status` flags.
