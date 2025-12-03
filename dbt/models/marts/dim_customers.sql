with customers as (
    select * from {{ ref('stg_customers') }}
)

select
    customer_id,
    customer_name,
    gender,
    date_of_birth,
    signup_date,
    email,
    address,

    -- Calculated Dimensions
   -- Calculate Customer Tenure
    datediff('year', date_of_birth, current_date()) as customer_age,

    _ingested_at,
    _loaded_at
from customers
