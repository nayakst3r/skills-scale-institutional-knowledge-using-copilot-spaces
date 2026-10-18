-- Usage per account, so billing doesn't have to join
select a.account_id, u.read_date, u.kwh
from {{ ref('metering_gold_daily_usage') }} u
join {{ ref('customer_gold_accounts') }} a on a.nmi = u.nmi
