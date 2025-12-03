with source as (
    select * from {{ source('raw_layer', 'customers') }}
),

renamed as (
    select
        customer_id,
        name as customer_name,
        gender,
        date_of_birth,
        signup_date,

        -- Standardize emails to lowercase
        -- Fix common domain typos (.om - .com, hotmai - hotmail)
        regexp_replace(
            regexp_replace(
                lower(email),
                '@(gmail|hotmail|yahoo)\\.om$', '@\\1.com'
            ),
            '@hotmai\\.com$', '@hotmail.com'
        ) as email,

        -- Fix multiline addresses (replace newline with space)
        replace(address, '\n', ' ') as address,

        _ingested_at,
        _loaded_at
    from source
)

select * from renamed
