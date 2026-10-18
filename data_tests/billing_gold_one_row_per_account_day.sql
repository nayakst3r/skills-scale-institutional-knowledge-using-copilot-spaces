-- Fails if an account is charged twice for the same day.
select account_id, read_date, count(*) as n
from {{ ref('billing_gold_daily_charges') }}
group by account_id, read_date
having count(*) > 1
