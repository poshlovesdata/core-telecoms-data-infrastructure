with agents as (
    select * from {{ ref('stg_agents') }}
)

select
    agent_id,
    agent_name,
    experience_level,
    state as agent_state,
    _ingested_at,
    _loaded_at
from agents
