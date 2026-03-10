import datetime
from enum import Enum
from typing import Annotated

from fastmcp import FastMCP

from cferates import Rate, get_rates_for


mcp = FastMCP(
    "cferates",
    instructions=(
        "MCP server for querying Mexican electricity rates from CFE "
        "(Comisión Federal de Electricidad). Provides current and "
        "historical rate information for domestic and industrial tariffs."
    ),
)


class RateName(str, Enum):
    """Available CFE rate names."""
    ONE = "1"
    ONE_A = "1A"
    ONE_B = "1B"
    ONE_C = "1C"
    ONE_D = "1D"
    ONE_E = "1E"
    ONE_F = "1F"
    DAC = "DAC"
    GDMTO = "GDMTO"
    RAMT = "RAMT"
    APMT = "APMT"
    GDMTH = "GDMTH"
    DIST = "DIST"
    DIT = "DIT"


_RATE_ENUM_MAP = {
    RateName.ONE: Rate.ONE,
    RateName.ONE_A: Rate.ONE_A,
    RateName.ONE_B: Rate.ONE_B,
    RateName.ONE_C: Rate.ONE_C,
    RateName.ONE_D: Rate.ONE_D,
    RateName.ONE_E: Rate.ONE_E,
    RateName.ONE_F: Rate.ONE_F,
    RateName.DAC: Rate.DAC,
    RateName.GDMTO: Rate.GDMTO,
    RateName.RAMT: Rate.RAMT,
    RateName.APMT: Rate.APMT,
    RateName.GDMTH: Rate.GDMTH,
    RateName.DIST: Rate.DIST,
    RateName.DIT: Rate.DIT,
}

DOMESTIC_RATES = {
    RateName.ONE, RateName.ONE_A, RateName.ONE_B, RateName.ONE_C,
    RateName.ONE_D, RateName.ONE_E, RateName.ONE_F, RateName.DAC,
}

SUMMER_RATES = {
    RateName.ONE_A, RateName.ONE_B, RateName.ONE_C,
    RateName.ONE_D, RateName.ONE_E, RateName.ONE_F,
}


@mcp.tool()
def get_cfe_rates(
    rate: Annotated[RateName, "The CFE rate tariff to query"],
    year: Annotated[int | None, "Year to query (default: current year)"] = None,
    month: Annotated[int | None, "Month to query, 1-12 (default: current month)"] = None,
    summer_month: Annotated[int | None, "Month when summer starts, 2-5 (required for rates 1A-1F)"] = None,
    state: Annotated[int | None, "State ID (required for industrial rates)"] = None,
    municipality: Annotated[int | None, "Municipality ID (required for industrial rates)"] = None,
    division: Annotated[int | None, "Division ID (required for industrial rates)"] = None,
) -> dict[str, str]:
    """Query CFE electricity rates for a given tariff, year, and month.

    Domestic rates (1, 1A-1F, DAC) are residential tariffs.
    Rates 1A-1F require the summer_month parameter.
    Industrial rates (GDMTO, RAMT, APMT, GDMTH, DIST, DIT) require
    state, municipality, and division IDs.
    """
    today = datetime.date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    if not 1 <= month <= 12:
        raise ValueError(f"month must be between 1 and 12, got {month}")
    if year < 2018 or year > today.year:
        raise ValueError(f"year must be between 2018 and {today.year}")

    if rate in SUMMER_RATES and summer_month is None:
        raise ValueError(f"summer_month is required for rate {rate.value}")
    if summer_month is not None and not 2 <= summer_month <= 5:
        raise ValueError(f"summer_month must be between 2 and 5, got {summer_month}")

    if rate not in DOMESTIC_RATES:
        if any(arg is None for arg in (state, municipality, division)):
            raise ValueError(
                "state, municipality, and division are required for industrial rates"
            )

    rate_enum = _RATE_ENUM_MAP[rate]
    return get_rates_for(
        rate_enum, year, month, summer_month, state, municipality, division
    )


@mcp.tool()
def list_cfe_rates() -> dict[str, list[str]]:
    """List all available CFE rate tariff names grouped by category."""
    return {
        "domestic": [r.value for r in sorted(DOMESTIC_RATES, key=lambda r: r.value)],
        "industrial": [
            r.value
            for r in sorted(
                set(RateName) - DOMESTIC_RATES, key=lambda r: r.value
            )
        ],
    }


def main():
    mcp.run()
