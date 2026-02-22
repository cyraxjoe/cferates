import os
import datetime
import pathlib
import json
from pprint import pprint

import click

from cferates import Rate, get_rates_for
from cferates._cli_cache import Cache


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
    'RAMT': Rate.RAMT,
    'APMT': Rate.APMT,
    'GDMTH': Rate.GDMTH,
    'DIST': Rate.DIST,
    'DIT': Rate.DIT,
}

def _verify_parameters(year: int, month: int, summer_month: int, rate: str,
                       state: int, municipality: int, division: int) -> None:
    rate_enum = _rate_mapping[rate]
    if rate_enum in (Rate.ONE, Rate.DAC) and summer_month is not None:
        raise click.BadOptionUsage(
            'summer_month',
            "The beginning of the summer is not relevant for the rate {}."
            .format(rate))

    # Check for industrial rates requirements
    domestic_rates = (Rate.ONE, Rate.DAC, Rate.ONE_A, Rate.ONE_B, Rate.ONE_C, Rate.ONE_D, Rate.ONE_E, Rate.ONE_F)
    if rate_enum not in domestic_rates:
        if not all((state, municipality, division)):
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
            _rate_mapping[rate], year, month, summer_month, state, municipality, division)
    else:
        app_dir = _ensure_app_dir()
        cache = Cache(app_dir)
        # TODO: Include state/mun/div in cache key
        transaction_key = (year, month, summer_month, rate, state, municipality, division)
        if transaction_key in cache:
            rates = cache[transaction_key]
        else:
            cache[transaction_key] = get_rates_for(
                _rate_mapping[rate], year, month, summer_month, state, municipality, division)
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
@click.argument('rate', type=click.Choice(tuple(_rate_mapping.keys())))
def main(year, month, summer_month, no_cache, rate, state, municipality, division):
    _verify_parameters(year, month, summer_month, rate, state, municipality, division)
    rates = get_rates(year, month, summer_month, no_cache, rate, state, municipality, division)
    click.echo(json.dumps(rates))
