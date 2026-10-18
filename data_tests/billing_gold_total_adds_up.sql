-- Fails if a total is more than a cent away from energy + supply + GST (rounding is per component).
select account_id, read_date, energy_charge_aud, supply_charge_aud, gst_aud, total_aud
from {{ ref('billing_gold_daily_charges') }}
where abs(total_aud - (energy_charge_aud + supply_charge_aud + gst_aud)) > 0.01
