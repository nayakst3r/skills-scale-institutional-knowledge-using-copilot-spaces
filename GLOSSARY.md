# Glossary

The shared language of this project. Use these terms exactly — in code, issues, specs and conversation with agents.
Add or change terms through `/plumbline grill`, which checks them against the code and existing decisions.

| Term | Meaning | Not to be confused with |
|---|---|---|
| NEM12 | AEMO's file format for interval meter data: 100 header, 200 meter details, 300 interval values, 900 end. | NEM13 (accumulation meters, not used here) |
| NMI | National Metering Identifier: the 10-character ID of a connection point (a premises' meter). | Meter serial number (the physical device) |
| Interval read | One meter value for one interval (5, 15 or 30 minutes) in kWh. | Daily usage (the sum of a day's interval reads) |
| Market time | AEST, UTC+10, with no daylight saving. All interval times are in market time. | Local time in Sydney or Melbourne (has daylight saving) |
| Quality method | The 300 record's flag: A actual, E estimated, S/F substitute, N null, V variable. | Data test (a dbt check) |
| Daily usage | Sum of a meter's interval reads for one market-time day (`metering_gold_daily_usage`). | Daily charge (usage priced by a tariff) |
| Daily charge | What one account owes for one day: energy + supply, plus GST shown separately. | Bill (a period's charges, produced elsewhere) |
