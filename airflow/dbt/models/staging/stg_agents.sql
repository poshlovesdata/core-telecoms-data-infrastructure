with source as (
    select * from {{ source('raw_layer', 'agents') }}
),

renamed as (
    select
        -- Rename messy ID columns to standard 'agent_id'
        id as agent_id,
        name as agent_name,
        experience as experience_level,
        state,

        _ingested_at,
        _loaded_at
    from source
)

select * from renamed
