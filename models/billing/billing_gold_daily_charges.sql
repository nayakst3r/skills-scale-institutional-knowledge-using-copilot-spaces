-- Published: what each account owes per market-time day. Energy at the account's tariff rate plus daily supply,
-- with GST (10%) shown separately. Only complete days are priced; incomplete days wait for the missing reads.
with usage as (
    select nmi, read_date, kwh, has_estimates
    from {{ ref('metering_gold_daily_usage') }}
    where is_complete
),

accounts as (
    select account_id, nmi, tariff_code, energy_rate_c_per_kwh, daily_supply_c
    from {{ ref('customer_gold_accounts') }}
),

priced as (
    select
        accounts.account_id,
        usage.nmi,
        usage.read_date,
        accounts.tariff_code,
        usage.kwh,
        usage.has_estimates,
        cast(round(usage.kwh * accounts.energy_rate_c_per_kwh / 100, 2) as decimal(18, 2)) as energy_charge_aud,
        cast(round(accounts.daily_supply_c / 100, 2) as decimal(18, 2))                    as supply_charge_aud
    from usage
    inner join accounts on accounts.nmi = usage.nmi
)

select
    account_id,
    nmi,
    read_date,
    tariff_code,
    kwh,
    has_estimates,
    energy_charge_aud,
    supply_charge_aud,
    cast(round((energy_charge_aud + supply_charge_aud) * 0.10, 2) as decimal(18, 2))       as gst_aud,
    cast(round((energy_charge_aud + supply_charge_aud) * 1.10, 2) as decimal(18, 2))       as total_aud
from priced
