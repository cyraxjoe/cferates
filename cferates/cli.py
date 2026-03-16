import os
import datetime
import pathlib
import json
import click

from cferates import Rate, get_rates_for, RATE_NAME_MAP
from cferates._cli_cache import Cache


def _verify_parameters(year: int, month: int, summer_month: int, rate: str,
                       state: int, municipality: int, division: int) -> None:
    rate_enum = RATE_NAME_MAP[rate]
    if rate_enum in (Rate.ONE, Rate.DAC) and summer_month is not None:
        raise click.BadOptionUsage(
            'summer_month',
            "The beginning of the summer is not relevant for the rate {}."
            .format(rate))

    # Check for industrial rates requirements
    domestic_rates = (Rate.ONE, Rate.DAC, Rate.ONE_A, Rate.ONE_B, Rate.ONE_C, Rate.ONE_D, Rate.ONE_E, Rate.ONE_F)
    if rate_enum not in domestic_rates:
        if any(arg is None for arg in (state, municipality, division)):
            raise click.UsageError("Options --state, --municipality and --division are required for industrial rates.")
    today =  datetime.date.today()
    if year < 2018 or year > today.year:
        raise click.BadOptionUsage(
            'year',
            "Invalid year: {}, not in between 2018 - [Current Year]."
            .format(year))
    if year == today.year and month > (today.month + 1):
        raise click.BadOptionUsage(
            'month',
            "Invalid month: {}, this month is too far away in the future (1 month tolerance)."
            .format(month))

def _ensure_app_dir():
    app_dir = click.get_app_dir('cferates')
    path = pathlib.Path(app_dir)
    if not path.exists():
        os.mkdir(path)
    return path


def get_rates(year, month, summer_month, no_cache, rate, state, municipality, division):
    if no_cache:
        rates = get_rates_for(
            RATE_NAME_MAP[rate], year, month, summer_month, state, municipality, division)
    else:
        app_dir = _ensure_app_dir()
        cache = Cache(app_dir)
        transaction_key = (year, month, summer_month, rate, state, municipality, division)
        if transaction_key in cache:
            rates = cache[transaction_key]
        else:
            cache[transaction_key] = get_rates_for(
                RATE_NAME_MAP[rate], year, month, summer_month, state, municipality, division)
            # retrieve the stringified version of the rates, as it was stored
            rates = cache[transaction_key]
    return rates


@click.command("cferates")
@click.option('--year', '-y', default=datetime.date.today().year,
              help="Year from which to query rate. Default is current year.")
@click.option('--month', '-m', default=datetime.date.today().month, type=click.IntRange(1, 12),
              help="Month as numberfrom which to query rate. Default is current month.")
@click.option('--summer-month', '-s', default=None, type=click.IntRange(2, 5),
              help="Month on which the summer starts at this rate (only rates: 1A - 1F)")
@click.option('--state', default=None, type=int, help="State ID (required for industrial rates)")
@click.option('--municipality', default=None, type=int, help="Municipality ID (required for industrial rates)")
@click.option('--division', default=None, type=int, help="Division ID (required for industrial rates)")
@click.option('--no-cache', default=False, is_flag=True,
              help="Disable cache")
@click.argument('rate', type=click.Choice(tuple(RATE_NAME_MAP.keys())))
def main(year, month, summer_month, no_cache, rate, state, municipality, division):
    _verify_parameters(year, month, summer_month, rate, state, municipality, division)
    rates = get_rates(year, month, summer_month, no_cache, rate, state, municipality, division)
    click.echo(json.dumps(rates))
