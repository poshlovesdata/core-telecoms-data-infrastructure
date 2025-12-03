with source as (
    select * from {{ source('raw_layer', 'social_media') }}
),

renamed as (
    select
        complaint_id,
        customer_id,
        agent_id,

        -- Fix source typo 'COMPLAINT_CATEGO_RY'
        complaint_catego_ry as complaint_category,

        -- Standardize status
        lower(resolutionstatus) as resolution_status,
        media_channel,

        -- Map dates
        request_date as submission_date,
        resolution_date,
        mediacomplaintgenerationdate as generated_date,

        _ingested_at,
        _loaded_at
    from source
)

select * from renamed
