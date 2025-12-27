-- incrementtal model for BTC transaction outputs
{{ config(
    materialized = 'incremental',
    incremental_strategy = 'append') }}

-- Select and flatten outputs from the BTC  table as CTE
with flattened_outputs as (

    select
        tx.HASH_KEY,
        tx.BLOCK_NUMBER,
        tx.BLOCK_TIMESTAMP,
        tx.IS_COINBASE,
        f.value:address::STRING AS output_address,
        f.value:value::FLOAT AS output_value
    from
        {{ ref('stg_btc') }} AS tx,
    LATERAL FLATTEN( input => outputs ) AS f
    where
        f.value:address IS NOT NULL

    -- incremental function check
    {% if is_incremental() %}
    and tx.BLOCK_TIMESTAMP >= (select max(BLOCK_TIMESTAMP) from {{ this }})
    {% endif %}
)

select
    HASH_KEY,
    BLOCK_NUMBER,
    BLOCK_TIMESTAMP,
    IS_COINBASE,
    output_address,
    output_value
from 
    flattened_outputs
