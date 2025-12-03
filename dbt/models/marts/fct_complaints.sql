with complaints as (
    select * from {{ ref('int_complaints_unioned') }}
)

select
    complaint_id,

    -- Foreign Keys (Connects to Dims)
    customer_id,
    agent_id,

    -- Measures & Attributes
    complaint_date,
    complaint_category,
    complaint_source,
    resolution_status,
    resolution_date,
    resolution_time_days,

    -- Metadata
    generated_date,
    _ingested_at
from complaints
