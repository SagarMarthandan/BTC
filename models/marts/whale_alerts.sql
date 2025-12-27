-- depends_on: {{ ref('btc_usd_max') }}

with WHALES as (
        select
        output_address,
        sum(output_value) as total_sent,
        count(*) as number_of_transactions
    from
        {{ ref('stg_btc_transactions') }}
    where
        output_value > 10
    group by
        output_address
    order by
        total_sent desc
)

select
    w.output_address,
    w.total_sent,
    w.number_of_transactions,
    {{ convert_to_usd('w.total_sent') }} as total_sent_usd 
from
    WHALES as w
order by
    w.total_sent desc