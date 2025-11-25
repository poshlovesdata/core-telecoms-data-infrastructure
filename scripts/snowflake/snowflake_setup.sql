-- 1. Create the Warehouse (The Compute Engine)
CREATE WAREHOUSE IF NOT EXISTS core_telecom_warehouse
WITH WAREHOUSE_SIZE = 'XSMALL'
AUTO_SUSPEND = 60
AUTO_RESUME = TRUE
INITIALLY_SUSPENDED = TRUE;


-- Create the Storage (Database & Schemas)
CREATE DATABASE IF NOT EXISTS core_telecom;

-- Schema for raw, messy data (Landing Zone)
CREATE SCHEMA IF NOT EXISTS core_telecom.raw;

-- Schema for clean, modeled data (dbt output)
CREATE SCHEMA IF NOT EXISTS core_telecom.curated;

-- Create a Custom Role for day-to-day tasks.
CREATE ROLE IF NOT EXISTS core_data_engineering;

-- Grant permissions to the role
GRANT USAGE ON WAREHOUSE core_telecom_warehouse TO ROLE core_data_engineering;
GRANT ALL ON DATABASE core_telecom TO ROLE core_data_engineering;
GRANT ALL ON SCHEMA core_telecom.raw TO ROLE core_data_engineering;
GRANT ALL ON SCHEMA core_telecom.curated TO ROLE core_data_engineering;

-- Create the Service User (for Airflow)
CREATE USER IF NOT EXISTS airflow_user
PASSWORD = 'coreTelAirflow!3'
DEFAULT_ROLE = core_data_engineering
DEFAULT_WAREHOUSE = core_telecom_warehouse;


-- Grant the role to the user
GRANT ROLE core_data_engineering TO USER airflow_user;

-- Verification
-- Run these to check if everything was created successfully
SHOW WAREHOUSES LIKE 'core_telecom_warehouse';
SHOW DATABASES LIKE 'core_telecom';
SHOW USERS LIKE 'airflow_user';
