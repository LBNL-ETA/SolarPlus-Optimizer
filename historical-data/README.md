# Historical data

Monthly CSV exports of the Solar+ site data, at 1-minute resolution, covering **2020-07-01 to 2021-08-31** (local time, America/Los_Angeles).

## Files

Each file is named `<start>to<end>.csv`, where `<start>` and `<end>` are local midnights.

- `old_host2020-07-01 …` through `old_host2020-12-01 …` were pulled from the old database host. The December file ends at **2020-12-21 04:00 UTC**.
- `2020-12-01 …` through `2021-08-01 …` were pulled from the new host. The December file starts at **2020-12-21 04:16 UTC**, so the two December files together cover the whole month.

The two hosts don't overlap. There is a 15-minute gap at the handoff.

## Format

- **Index (first, unnamed column):** timestamp in **UTC** (e.g. `2020-07-01 07:00:00+00:00`), one row per minute. Because the file boundaries are local midnights, each file starts at 07:00 or 08:00 UTC, depending on daylight saving time.

### Columns

| # | Name | Group | Description | Units |
|---|---|---|---|---|
| 1 | building | Power | Building main meter | W |
| 2 | freezer | Power | Freezer compressor + evaporator fan | W |
| 3 | ref_comp | Power | Refrigerator compressor | W |
| 4 | ref_fan | Power | Refrigerator evaporator fan | W |
| 5 | hvac_west | Power | West HVAC compressor | W |
| 6 | hvac_east | Power | East HVAC compressor | W |
| 7 | pv_generation | Power | Measured PV generation | W |
| 9 | MPC_battery | Battery (MPC) | Battery power setpoint from the battery emulated in the MPC | W |
| 10 | MPC_soc | Battery (MPC) | State of charge of the battery emulated in the MPC | fraction (0.25–0.95) |
| 11 | east | Temperature | East zone temperature | °F |
| 12 | west | Temperature | West zone temperature | °F |
| 13 | freezer | Temperature | Freezer cabinet temperature | °F |
| 14 | ref | Temperature | Refrigerator cabinet temperature | °F |
| 15 | east_heating | Setpoint | East heating setpoint | °F |
| 16 | east_cooling | Setpoint | East cooling setpoint | °F |
| 17 | west_heating | Setpoint | West heating setpoint | °F |
| 18 | west_cooling | Setpoint | West cooling setpoint | °F |
| 19 | freezer | Setpoint | Freezer setpoint | °F |
| 20 | ref | Setpoint | Refrigerator setpoint | °F |
| 21 | soc | Battery | Same as `MPC_soc` (identical in every row) | fraction |
| 22 | setpoint | Battery | Same as `MPC_battery` (identical in every row) | W |
| 23 | pv_generation | Battery | PV value used by the MPC. Not the same as the measured PV (column 7): they match only at night, when both are 0 | W |
| 24 | oat | Weather (observed) | Outside air temperature | °F |
| 25 | humidity | Weather (observed) | Relative humidity | % |
| 26 | windspeed | Weather (observed) | Wind speed (Dark Sky API) | mph |
| 27 | cloudcover | Weather (observed) | Cloud cover | fraction (0–1) |
| 28 | solar | Weather (observed) | Solar irradiance | W/m² |
| 29 | sr | Weather (observed) | Same as `solar` (identical in every row) | W/m² |
| 30 | oat | Weather (forecast) | Forecast outside air temperature | °F |
| 31 | humidity | Weather (forecast) | Forecast relative humidity | % |
| 32 | windspeed | Weather (forecast) | Forecast wind speed (Dark Sky API) | mph |
| 33 | cloudcover | Weather (forecast) | Forecast cloud cover | fraction (0–1) |
| 34 | solar | Weather (forecast) | Forecast solar irradiance | W/m² |
| 35 | price_energy | Price / DR | Energy price (PG&E B-19 tariff) | $/kWh |
| 36 | price_demand | Price / DR | Demand charge | $/kW |
| 37 | pmax | Price / DR | Maximum power limit (±999,999 means no limit) | W |
| 38 | pmin | Price / DR | Minimum power limit (±999,999 means no limit) | W |

## Loading

```python
import glob
import pandas as pd

names = [
    "building", "freezer_power", "ref_comp_power", "ref_fan_power", "hvac_west_power", "hvac_east_power",
    "pv_generation", "current_stored_energy", "MPC_battery", "MPC_soc",
    "east_temp", "west_temp", "freezer_temp", "ref_temp",
    "east_heating_sp", "east_cooling_sp", "west_heating_sp", "west_cooling_sp", "freezer_sp", "ref_sp",
    "battery_soc", "battery_setpoint", "battery_pv_generation",
    "oat", "humidity", "windspeed", "cloudcover", "solar", "sr",
    "oat_forecast", "humidity_forecast", "windspeed_forecast", "cloudcover_forecast", "solar_forecast",
    "price_energy", "price_demand", "pmax", "pmin",
]

df = pd.concat(
    pd.read_csv(f, header=None, skiprows=1, index_col=0, names=["time"] + names, parse_dates=["time"])
    for f in sorted(glob.glob("*.csv"))
).sort_index().drop(columns="current_stored_energy")
df = df.tz_convert("America/Los_Angeles")  # optional: switch to local time
```
