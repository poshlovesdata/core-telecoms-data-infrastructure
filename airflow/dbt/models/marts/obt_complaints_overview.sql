with enriched as (
    select * from {{ ref('int_complaints_enriched') }}
)

select
    -- All columns from the enriched table
    *
from enriched
