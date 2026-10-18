-- Raw interval reads exactly as ingested from NEM12 files. Append-only; no typing or filtering here.
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
from {{ source('landing', 'interval_reads') }}
