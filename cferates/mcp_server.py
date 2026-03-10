import datetime
import json

from mcp.server.fastmcp import FastMCP

from cferates import Rate, get_rates_for


_rate_mapping = {
    '1': Rate.ONE,
    '1A': Rate.ONE_A,
    '1B': Rate.ONE_B,
    '1C': Rate.ONE_C,
    '1D': Rate.ONE_D,
    '1E': Rate.ONE_E,
    '1F': Rate.ONE_F,
    'DAC': Rate.DAC,
    'GDMTO': Rate.GDMTO,
    'GDMTH': Rate.GDMTH,
    'DIST': Rate.DIST,
    'DIT': Rate.DIT,
    'APMT': Rate.APMT,
    'RAMT': Rate.RAMT,
}

_DOMESTIC_RATES = {'1', '1A', '1B', '1C', '1D', '1E', '1F', 'DAC'}
_SUMMER_RATES = {'1A', '1B', '1C', '1D', '1E', '1F'}

mcp = FastMCP(
    "cferates",
    instructions="Query electricity rates from Mexico's CFE (Comisión Federal de Electricidad)",
)


def _validate_parameters(
    rate_upper: str,
    year: int,
    month: int,
    summer_month: int | None,
) -> str | None:
    """Validate input parameters, returning an error message or None if valid."""
    today = datetime.date.today()
    if year < 2018 or year > today.year:
        return f"Invalid year: {year}. Must be between 2018 and {today.year}."
    if month < 1 or month > 12:
        return f"Invalid month: {month}. Must be between 1 and 12."
    if year == today.year and month > today.month + 1:
        return f"Invalid month: {month} is too far in the future (1 month tolerance)."
    if rate_upper in _SUMMER_RATES and summer_month is not None:
        if summer_month < 2 or summer_month > 5:
            return f"Invalid summer_month: {summer_month}. Must be between 2 and 5."
    if rate_upper in ('1', 'DAC') and summer_month is not None:
        return f"summer_month is not relevant for rate {rate_upper}."
    return None


@mcp.tool()
def list_rates() -> str:
    """List all available CFE rate types.

    Returns the available rate identifiers grouped by category:
    - Domestic rates: 1, 1A-1F, DAC
    - Industrial rates: GDMTO, GDMTH, DIST, DIT, APMT, RAMT

    Domestic rates 1A-1F require a summer_month parameter.
    Industrial rates require state, municipality, and division parameters.
    """
    return json.dumps({
        "domestic": {
            "simple": ["1", "DAC"],
            "with_summer": ["1A", "1B", "1C", "1D", "1E", "1F"],
        },
        "industrial": ["GDMTO", "GDMTH", "DIST", "DIT", "APMT", "RAMT"],
        "notes": {
            "summer_month": "Required for rates 1A-1F. The month (2-5) when summer starts in the locality.",
            "state_municipality_division": "Required for industrial rates. IDs correspond to CFE website form values.",
        },
    }, indent=2)


@mcp.tool()
def get_rates(
    rate: str,
    year: int | None = None,
    month: int | None = None,
    summer_month: int | None = None,
    state: int | None = None,
    municipality: int | None = None,
    division: int | None = None,
) -> str:
    """Get CFE electricity rates for a given rate type, year, and month.

    Args:
        rate: The rate type to query. Use list_rates() to see available options.
              Domestic: 1, 1A, 1B, 1C, 1D, 1E, 1F, DAC.
              Industrial: GDMTO, GDMTH, DIST, DIT, APMT, RAMT.
        year: Year to query (default: current year). Must be >= 2018.
        month: Month to query, 1-12 (default: current month).
        summer_month: Month when summer starts (2-5). Required for rates 1A-1F.
        state: State ID (1-32). Required for industrial rates.
        municipality: Municipality ID. Required for industrial rates.
        division: Division ID. Required for industrial rates.

    Returns:
        JSON string with rate components (e.g. Basico, Intermedio, Excedente for
        domestic rates, or fijo, variable, distribucion, capacidad for industrial).
    """
    today = datetime.date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    rate_upper = rate.upper()
    if rate_upper not in _rate_mapping:
        return json.dumps({
            "error": f"Unknown rate '{rate}'. Valid rates: {', '.join(sorted(_rate_mapping.keys()))}"
        })

    if rate_upper in _SUMMER_RATES and summer_month is None:
        return json.dumps({
            "error": f"summer_month (2-5) is required for rate {rate_upper}"
        })

    if rate_upper not in _DOMESTIC_RATES:
        if any(arg is None for arg in (state, municipality, division)):
            return json.dumps({
                "error": f"state, municipality, and division are required for rate {rate_upper}"
            })

    validation_error = _validate_parameters(rate_upper, year, month, summer_month)
    if validation_error:
        return json.dumps({"error": validation_error})

    rate_enum = _rate_mapping[rate_upper]
    try:
        result = get_rates_for(
            rate_enum, year, month,
            summer_month=summer_month,
            state=state,
            municipality=municipality,
            division=division,
        )
    except Exception as e:
        return json.dumps({"error": str(e)})

    return json.dumps(result)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
