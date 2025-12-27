{{ config(materialized = 'ephemeral')}}
-- Select and flatten outputs from the BTC staging table as CTE

select
    *
from
    {{ ref('stg_btc_outputs') }}
where
    IS_COINBASE = false