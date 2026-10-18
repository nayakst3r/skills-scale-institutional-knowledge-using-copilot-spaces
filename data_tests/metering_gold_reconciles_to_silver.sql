-- Fails if daily totals don't add up to the interval reads they came from (quality attribute 1: correctness).
with gold as (select sum(kwh) as kwh from {{ ref('metering_gold_daily_usage') }}),
silver as (
    select sum(kwh) as kwh from {{ ref('metering_silver_interval_reads') }}
    where uom = 'KWH' and nmi_suffix like 'E%'
)
select gold.kwh as gold_kwh, silver.kwh as silver_kwh
from gold cross join silver
where gold.kwh <> silver.kwh
