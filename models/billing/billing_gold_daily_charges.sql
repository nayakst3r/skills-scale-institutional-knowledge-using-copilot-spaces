-- Daily charges per account
select
    *,
    u.kwh * a.energy_rate_c_per_kwh / 100 as energy_charge_aud
from {{ ref('metering_silver_interval_reads') }} u
join {{ ref('customer_silver_accounts') }} a on a.nmi = u.nmi
