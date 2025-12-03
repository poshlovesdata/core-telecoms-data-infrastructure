with source as (
    select * from {{ source('raw_layer', 'call_logs') }}
),

renamed as (
    select
        call_id,
        customer_id,
        agent_id,

        -- Fix source typo
        complaint_catego_ry as complaint_category,

        -- Standardize status
        lower(resolutionstatus) as resolution_status,

        -- Timestamps
        call_start_time,
        call_end_time,

        calllogsgenerationdate as generated_date,
        _ingested_at,
        _loaded_at
    from source
    -- Filter out potential bad rows where IDs are null
    where call_id is not null
)

select * from renamed
