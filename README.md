.. -*- rst -*-
##################
CFE rates scraper
##################

A Python library and CLI tool to scrape energy prices from the Mexico CFE (Comisión Federal de Electricidad) website.

Installation
============

You can install the package using uv:

.. code-block:: bash

    uv sync

Usage
=====

CLI
---

The package provides a `cferates` command.

Domestic Rates
~~~~~~~~~~~~~~

For domestic rates (1, 1A-1F, DAC):

.. code-block:: bash

    # Rate 1
    uv run cferates 1

    # Rate 1A with summer starting in February
    uv run cferates 1A --summer-month 2

Industrial Rates
~~~~~~~~~~~~~~~~

For industrial rates (GDMTO, GDMTH, etc.), you must provide the State, Municipality, and Division IDs. These IDs correspond to the values used in the CFE website forms.

.. code-block:: bash

    uv run cferates GDMTO --state <ID> --municipality <ID> --division <ID>

Options
~~~~~~~

- `-y`, `--year`: Year to query (default: current year).
- `-m`, `--month`: Month to query (default: current month).
- `-s`, `--summer-month`: Start month of summer (required for 1A-1F).
- `--state`: State ID (required for industrial rates).
- `--municipality`: Municipality ID (required for industrial rates).
- `--division`: Division ID (required for industrial rates).
- `--no-cache`: Disable caching of results.

Library Usage
-------------

You can also use the library in your Python code:

.. code-block:: python

    from cferates import Rate, get_rates_for

    # Domestic
    rates = get_rates_for(Rate.ONE, 2023, 1)
    print(rates)

    # Industrial
    rates = get_rates_for(Rate.GDMTO, 2023, 1, state=1, municipality=2, division=3)
    print(rates)

Development
===========

Running Tests
-------------

.. code-block:: bash

    uv run pytest

Environment Variables
---------------------

- `CFERATES_NO_DELAY`: Set to 1 to disable the delay between requests in the industrial scraper (useful for testing).
