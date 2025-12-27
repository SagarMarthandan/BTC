with BASE as (
    select *
    from {{ ref('whale_alerts') }}
    order by total_sent desc
    limit 10
)

select * from BASE