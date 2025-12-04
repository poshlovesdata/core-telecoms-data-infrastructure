-- Admin user
CREATE OR REPLACE STORAGE INTEGRATION coretelecoms_s3_init
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = 'S3'
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::669155637899:role/core-telecoms-snowflake-role'
    STORAGE_ALLOWED_LOCATIONS = ('s3://cde-core-telecoms-data-lake/');

GRANT USAGE ON INTEGRATION coretelecoms_s3_init TO ROLE core_data_engineering;

DESC INTEGRATION coretelecoms_s3_init;



-- Switch to airflow_user
USE ROLE core_data_engineering;
USE WAREHOUSE core_telecom_warehouse;
USE DATABASE core_telecom;
USE SCHEMA raw;

-- Create parquet file format
CREATE OR REPLACE FILE FORMAT parquet_format
    TYPE = 'PARQUET'
    COMPRESSION = 'SNAPPY';

-- Connect to S3
CREATE OR REPLACE STAGE coretelecom_s3_stage
    STORAGE_INTEGRATION = coretelecoms_s3_init
    URL = 's3://cde-core-telecoms-data-lake/'
    FILE_FORMAT = parquet_format;

DESC INTEGRATION coretelecoms_s3_init;

-- Define Raw Tables

-- Agents
CREATE OR REPLACE TABLE agents (
    id VARCHAR,
    name VARCHAR,
    experience VARCHAR,
    state VARCHAR,
    _ingested_at TIMESTAMP_NTZ,
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Customers
CREATE OR REPLACE TABLE customers (
    customer_id VARCHAR,
    name VARCHAR,
    gender VARCHAR,
    date_of_birth DATE,
    signup_date DATE,
    email VARCHAR,
    address VARCHAR,
    _ingested_at TIMESTAMP_NTZ,
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Web Forms
CREATE OR REPLACE TABLE web_forms (
    column1 VARCHAR,
    request_id VARCHAR,
    customer_id VARCHAR,
    complaint_catego_ry VARCHAR,
    agent_id VARCHAR,
    resolutionstatus VARCHAR,
    request_date DATE,
    resolution_date DATE,
    webformgenerationdate DATE,
    _ingested_at TIMESTAMP_NTZ,
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Call Center
CREATE OR REPLACE TABLE call_logs (
    unnamed__0 VARCHAR,
    call_id VARCHAR,
    customer_id VARCHAR,
    complaint_catego_ry VARCHAR,
    agent_id VARCHAR,
    call_start_time TIMESTAMP_NTZ,
    call_end_time TIMESTAMP_NTZ,
    resolutionstatus VARCHAR,
    calllogsgenerationdate DATE,
    _ingested_at TIMESTAMP_NTZ,
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Social Media
CREATE OR REPLACE TABLE social_media (
    complaint_id VARCHAR,
    customer_id VARCHAR,
    complaint_catego_ry VARCHAR,
    agent_id VARCHAR,
    resolutionstatus VARCHAR,
    request_date DATE,
    resolution_date DATE,
    media_channel VARCHAR,
    mediacomplaintgenerationdate DATE,
    _ingested_at TIMESTAMP_NTZ,
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

LIST @coretelecom_s3_stage;

SELECT * FROM raw.agents limit 10;
SELECT * FROM raw.customers limit 10;
SELECT * FROM raw.web_forms limit 10;
SELECT * FROM raw.social_media limit 10;
SELECT * FROM raw.call_logs limit 10;

DESC TABLE core_telecom.raw.web_forms;

SHOW SCHEMAS;

SELECT * FROM core_telecom.public_staging.stg_web_forms ;
-- LIMIT 10000;
SELECT * FROM core_telecom.public_staging.stg_call_logs
LIMIT 10;

SELECT * FROM core_telecom.public_staging.stg_social_media
LIMIT 100;

SELECT * FROM core_telecom.analytics.int_complaints_unioned ;

SELECT * FROM core_telecom.analytics.int_complaints_unioned
LIMIT 100;

SELECT * FROM core_telecom.analytics_marts.dim_agents
LIMIT 100;
