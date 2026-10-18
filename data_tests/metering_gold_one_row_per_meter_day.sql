-- Fails if a meter has more than one daily-usage row for the same day.
select nmi, read_date, count(*) as n
from {{ ref('metering_gold_daily_usage') }}
group by nmi, read_date
having count(*) > 1
