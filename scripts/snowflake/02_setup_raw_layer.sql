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
    _ingested_at TIMESTAMP_NTZ
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
    _ingested_at TIMESTAMP_NTZ
);

-- Web Forms
-- Note: 'column1' and 'complaint_catego_ry' come from source messiness
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
    _ingested_at TIMESTAMP_NTZ
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
    _ingested_at TIMESTAMP_NTZ
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
    _ingested_at TIMESTAMP_NTZ
);

LIST @coretelecom_s3_stage;
