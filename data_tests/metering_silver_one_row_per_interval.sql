-- Fails if any meter stream has more than one row for the same interval.
select nmi, nmi_suffix, interval_start, count(*) as n
from {{ ref('metering_silver_interval_reads') }}
group by nmi, nmi_suffix, interval_start
having count(*) > 1
