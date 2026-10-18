-- Published: one row per account with its meter and tariff. No personal data leaves the customer domain.
select
    account_id,
    nmi,
    tariff_code,
    energy_rate_c_per_kwh,
    daily_supply_c
from {{ ref('customer_silver_accounts') }}
