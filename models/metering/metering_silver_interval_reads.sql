-- Typed and de-duplicated: one row per meter stream per interval. A re-sent file replaces earlier values.
with typed as (
    select
        nmi,
        nmi_suffix,
        upper(uom)                              as uom,
        cast(interval_minutes as integer)       as interval_minutes,
        cast(read_date as date)                 as read_date,
        cast(interval_number as integer)        as interval_number,
        cast(interval_start as timestamp)       as interval_start,
        cast(kwh as decimal(18, 3))             as kwh,
        quality,
        source_file,
        cast(source_line as integer)            as source_line
    from {{ ref('metering_bronze_interval_reads') }}
),

ranked as (
    select
        *,
        row_number() over (
            partition by nmi, nmi_suffix, interval_start
            order by source_file desc, source_line desc
        ) as version_rank
    from typed
)

select
    nmi,
    nmi_suffix,
    uom,
    interval_minutes,
    read_date,
    interval_number,
    interval_start,
    kwh,
    quality,
    source_file,
    source_line
from ranked
where version_rank = 1
