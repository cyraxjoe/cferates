---
name: cfe-rates
description: Look up CFE (Mexico) electricity rates. Use when the user asks about electricity rates, tariffs, energy costs, or CFE pricing.
---

# CFE Electricity Rate Lookup

You have access to the `cferates` CLI tool to query electricity rates from Mexico's CFE (Comisión Federal de Electricidad).

## Setup

First, check if the local marketplace checkout exists at `~/.claude/plugins/marketplaces/cferates/`. If it does, use it as the source. If not, fall back to the remote repository.

```bash
if [ -d ~/.claude/plugins/marketplaces/cferates ]; then
    CFERATES_SRC=~/.claude/plugins/marketplaces/cferates
else
    CFERATES_SRC=git+https://github.com/cyraxjoe/cferates.git
fi
```

Then run with `uvx`:

```bash
uvx --from "$CFERATES_SRC" cferates RATE [OPTIONS]
```

## Rate Types

### Domestic
| Rate | Description | Requirements |
|------|-------------|--------------|
| `1` | Basic domestic | None |
| `DAC` | High-consumption domestic (no subsidy) | None |
| `1A`–`1F` | Regional domestic with summer variation | `--summer-month` required |

### Industrial
| Rate | Description | Requirements |
|------|-------------|--------------|
| `GDMTO` | Gran Demanda Media Tensión Ordinaria | `--state`, `--municipality`, `--division` |
| `GDMTH` | Gran Demanda Media Tensión Horaria | `--state`, `--municipality`, `--division` |
| `DIST` | Demanda Industrial Subtransmisión | `--state`, `--municipality`, `--division` |
| `DIT` | Demanda Industrial Transmisión | `--state`, `--municipality`, `--division` |
| `APMT` | Alumbrado Público Media Tensión | `--state`, `--municipality`, `--division` |
| `RAMT` | Riego Agrícola Media Tensión | `--state`, `--municipality`, `--division` |

## Options

- `-y, --year YEAR` — Year to query (default: current year, min: 2018)
- `-m, --month MONTH` — Month to query (default: current month, 1–12)
- `-s, --summer-month MONTH` — Month summer starts (2–5). Required for rates 1A–1F
- `--state ID` — State ID (1–32). Required for industrial rates
- `--municipality ID` — Municipality ID. Required for industrial rates
- `--division ID` — Division ID. Required for industrial rates
- `--no-cache` — Disable caching

## Common City → Rate Mapping

Use this to infer the rate type when the user mentions a city:

| City/Region | Typical Rate | Summer Month |
|-------------|-------------|--------------|
| Mexico City / Central Highlands | 1 | N/A |
| Monterrey / Nuevo León | 1C | 4 |
| Guadalajara / Jalisco | 1 | N/A |
| Hermosillo / Sonora | 1F | 3 |
| Mexicali / Baja California | 1F | 3 |
| Mérida / Yucatán | 1D | 4 |
| Culiacán / Sinaloa | 1E | 3 |
| Tampico / Tamaulipas | 1D | 4 |
| Ciudad Juárez / Chihuahua | 1C | 4 |
| Cancún / Quintana Roo | 1C | 4 |

## Output

The CLI returns JSON. Domestic rates include keys like `Basico`, `Intermedio`, `Excedente` (values in MXN/kWh). Industrial rates include keys like `fijo`, `variable`, `distribucion`, `capacidad`.

## DAC Threshold Awareness

When discussing DAC (Doméstica de Alto Consumo) classification, do NOT assume a single universal threshold. Each domestic tariff has its own DAC limit:

| Tarifa | DAC Threshold |
|--------|---------------|
| 1      | 250 kWh/mes   |
| 1A     | 300 kWh/mes   |
| 1B     | 400 kWh/mes   |
| 1C     | 850 kWh/mes   |
| 1D     | 1,000 kWh/mes |
| 1E     | 2,000 kWh/mes |
| 1F     | 2,500 kWh/mes |

Source: https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/TarifaDAC.aspx

The threshold varies significantly by region/climate — hotter regions (1E, 1F) allow much higher consumption before DAC kicks in because air conditioning is expected. A user in Monterrey (1C) can consume up to 850 kWh/month before being reclassified, while a user in Mexico City (tarifa 1) hits DAC at just 250 kWh/month.

DAC is triggered when the user's **12-month rolling average** exceeds their tariff's threshold — not a single month's spike.

When warning users about DAC risk:
1. First identify their tariff from the city mapping
2. Use the correct threshold for that specific tariff
3. If the user provides historical consumption, calculate their 12-month average and compare against the correct threshold before making any DAC claims

## Instructions

1. When the user mentions a city, map it to the appropriate rate and summer_month using the table above. If unsure, ask.
2. Run the CLI command and present the results in a readable table.
3. Briefly explain what each tier means (Básico = first ~75 kWh subsidized, Intermedio = next block, Excedente = above that, most expensive).
4. Only mention DAC risk if the user provides consumption data — use the correct threshold for their specific tariff (see table above), not a generic 250 kWh value.
