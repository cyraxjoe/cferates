---
name: cfe-rates
description: Look up CFE (Mexico) electricity rates. Use when the user asks about electricity rates, tariffs, energy costs, or CFE pricing.
---

# CFE Electricity Rate Lookup

You have access to the `cferates` CLI tool to query electricity rates from Mexico's CFE (Comisión Federal de Electricidad).

## CLI Usage

```
cferates RATE [OPTIONS]
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

## Instructions

1. When the user mentions a city, map it to the appropriate rate and summer_month using the table above. If unsure, ask.
2. Run the CLI command and present the results in a readable table.
3. Briefly explain what each tier means (Básico = first ~75 kWh subsidized, Intermedio = next block, Excedente = above that, most expensive).
4. If the user's consumption seems high, mention the DAC threshold risk.
