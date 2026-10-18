-- Published: daily consumption per meter (market time). A day is complete when every interval is present.
select
    nmi,
    read_date,
    sum(kwh)                                                    as kwh,
    count(*)                                                    as intervals,
    count(*) filter (where quality = 'A')                       as actual_intervals,
    count(*) = max(1440 / interval_minutes)                     as is_complete,
    bool_or(quality <> 'A')                                     as has_estimates
from {{ ref('metering_silver_interval_reads') }}
where uom = 'KWH' and nmi_suffix like 'E%'
group by nmi, read_date
