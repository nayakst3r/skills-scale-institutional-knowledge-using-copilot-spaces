-- Typed customer accounts from the CRM extract. Contains personal data (email): stays in the customer domain.
select
    account_id,
    nmi,
    tariff_code,
    cast(energy_rate_c_per_kwh as decimal(10, 4))   as energy_rate_c_per_kwh,
    cast(daily_supply_c as decimal(10, 4))          as daily_supply_c,
    lower(email)                                    as email
from {{ ref('customer_raw_accounts') }}
