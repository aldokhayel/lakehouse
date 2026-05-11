-- Mart model: daily revenue aggregation.
-- Aggregates completed orders by date for business reporting.

with orders as (
    select * from {{ ref('stg_orders') }}
    where is_complete = true
)

select
    order_date,
    count(*)                    as order_count,
    sum(amount_usd)             as total_revenue,
    avg(amount_usd)             as avg_order_value,
    min(amount_usd)             as min_order_value,
    max(amount_usd)             as max_order_value
from orders
group by order_date
order by order_date
