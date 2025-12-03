with web_forms as (
    select
        request_id as complaint_id,
        customer_id,
        agent_id,
        complaint_category,
        resolution_status,
        submission_date as complaint_date,
        resolution_date,
        'Web Form' as complaint_source,
        generated_date,
        _ingested_at,
        _loaded_at
    from {{ ref('stg_web_forms') }}
),

call_logs as (
    select
        call_id as complaint_id,
        customer_id,
        agent_id,
        complaint_category,
        resolution_status,
        call_start_time as complaint_date,

        case
            when lower(resolution_status) = 'resolved' then call_end_time::date
            else null
        end as resolution_date,

        'Call Center' as complaint_source,
        generated_date,
        _ingested_at,
        _loaded_at
    from {{ ref('stg_call_logs') }}
),

social_media as (
    select
        complaint_id,
        customer_id,
        agent_id,
        complaint_category,
        resolution_status,
        submission_date as complaint_date,
        resolution_date,
        concat('Social - ', media_channel) as complaint_source,
        generated_date,
        _ingested_at,
        _loaded_at
    from {{ ref('stg_social_media') }}
),

unioned as (
    select * from web_forms
    union all
    select * from call_logs
    union all
    select * from social_media
)

select
    *,
    -- Business Logic: Calculate Resolution Time
    datediff('day', complaint_date, resolution_date) as resolution_time_days
from unioned
