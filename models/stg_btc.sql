{{ config(
    materialized = 'incremental',
    unique_key = 'HASH_KEY',
    incremental_strategy = 'merge') }}

select
    *
from
    {{ source('btc', 'btc') }}

{% if is_incremental() %}

where BLOCK_TIMESTAMP >= (select max(BLOCK_TIMESTAMP) from {{ this }})

{% endif %}