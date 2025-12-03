with source as (
    select * from {{ source('raw_layer', 'web_forms') }}
),

renamed as (
    select
        request_id,
        customer_id,
        agent_id,

        -- Fix the messy source column name
        complaint_catego_ry as complaint_category,

        -- Standardize status to lowercase
        lower(resolutionstatus) as resolution_status,


        request_date as submission_date,

        resolution_date,

        -- Rename for readability
        webformgenerationdate as generated_date,

        _ingested_at,
        _loaded_at
    from source
)

select * from renamed
