with complaints as (
    select * from {{ ref('int_complaints_unioned') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

agents as (
    select * from {{ ref('stg_agents') }}
),

enriched as (
    select
        -- Key IDs
        c.complaint_id,
        c.customer_id,
        c.agent_id,

        -- Complaint Details
        c.complaint_date,
        c.complaint_category,
        c.complaint_source,
        c.resolution_status,
        c.resolution_date,
        c.resolution_time_days,

        -- Customer Details (Joined)
        cust.customer_name,
        cust.email as customer_email,
        cust.gender,
        cust.date_of_birth,

        -- Agent Details (Joined)
        a.agent_name,
        a.experience_level as agent_experience,
        a.state as agent_state,

        -- Metadata
        c._ingested_at

    from complaints c
    left join customers cust
        on c.customer_id = cust.customer_id
    left join agents a
        on c.agent_id = a.agent_id
)

select * from enriched
