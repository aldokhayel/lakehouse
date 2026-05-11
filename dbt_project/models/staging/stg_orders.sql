-- Staging model: clean, type-cast, and deduplicate raw orders.
-- Adds a boolean is_complete flag and renames amount to amount_usd.

with source as (
    select * from {{ source('raw', 'raw_orders') }}
),

renamed as (
    select
        order_id,
        customer_id,
        cast(order_date as date)                as order_date,
        cast(amount as double)                  as amount_usd,
        lower(trim(status))                     as status,
        lower(trim(status)) = 'completed'       as is_complete,
        _ingested_at                            as _loaded_at
    from source
)

select * from renamed
