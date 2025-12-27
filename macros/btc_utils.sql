-- Macro to convert BTC values to USD using the latest BTC to USD price
{% macro convert_to_usd(column_name) %}

{{column_name}} * (    
    select price 
    from {{ ref('btc_usd_max') }}
    where to_date(replace(snapped_at, 'UTC','')) = current_date()
)

{% endmacro %}