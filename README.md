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

**Note on `--summer-month`:**
The CFE determines the start of the summer subsidy based on historical temperature data for each specific locality. According to the *Ley de la Industria Eléctrica* (Electric Industry Law), the supplier (CFE) fixes the "six consecutive warmest months" based on thermometric observations provided by SEMARNAT (Ministry of Environment and Natural Resources).

Because this is an administrative determination published annually via tariff agreements in the *Diario Oficial de la Federación (DOF)*—and occasionally modified by state agreements—there is no official, up-to-date API or static legal table mapping every Mexican municipality to its specific summer start month.

Therefore, you must manually provide the month (between `2` for February and `5` for May) when the summer rate begins in your area.

For example, summer usually starts in **May (5)** for Monterrey, and recently starts in **April (4)** for Hermosillo and all of Sonora due to a state-wide agreement.

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

Español
=======

Una librería de Python y herramienta de línea de comandos (CLI) para obtener los precios de la energía de la página web de la Comisión Federal de Electricidad (CFE) de México.

Instalación
-----------

Puedes instalar el paquete utilizando uv:

.. code-block:: bash

    uv sync

Uso
---

CLI
~~~

El paquete provee el comando `cferates`.

Tarifas Domésticas
^^^^^^^^^^^^^^^^^^

Para tarifas domésticas (1, 1A-1F, DAC):

.. code-block:: bash

    # Tarifa 1
    uv run cferates 1

    # Tarifa 1A con inicio de verano en febrero
    uv run cferates 1A --summer-month 2

**Nota sobre `--summer-month` (mes de verano):**
La CFE determina el inicio del subsidio de verano basándose en los datos históricos de temperatura de cada localidad específica. Según la *Ley de la Industria Eléctrica*, el Suministrador (CFE) fija cuáles son los "seis meses consecutivos más cálidos del año" tomando como base las observaciones termométricas expedidas por la SEMARNAT (Secretaría de Medio Ambiente y Recursos Naturales).

Dado que esto es una determinación administrativa publicada año con año mediante Acuerdos Tarifarios en el *Diario Oficial de la Federación (DOF)* —y que en ocasiones es modificada mediante convenios estatales—, no existe una API centralizada, oficial y actualizada, ni una tabla estática en la ley que mapee cada municipio a su mes de inicio de verano.

Por lo tanto, debes proveer manualmente el mes (entre `2` para febrero y `5` para mayo) en que comienza la tarifa de verano en tu área.

Por ejemplo, el verano suele iniciar en **Mayo (5)** para Monterrey, y recientemente inicia en **Abril (4)** para Hermosillo y todo Sonora gracias a un convenio estatal.

Tarifas Industriales
^^^^^^^^^^^^^^^^^^^^

Para las tarifas industriales (GDMTO, GDMTH, etc.), debes proveer los IDs de Estado, Municipio y División. Estos IDs corresponden a los valores utilizados en los formularios de la página web de la CFE.

.. code-block:: bash

    uv run cferates GDMTO --state <ID> --municipality <ID> --division <ID>

Opciones
^^^^^^^^

- `-y`, `--year`: Año a consultar (por defecto: año actual).
- `-m`, `--month`: Mes a consultar (por defecto: mes actual).
- `-s`, `--summer-month`: Mes de inicio de verano (requerido para 1A-1F).
- `--state`: ID de Estado (requerido para tarifas industriales).
- `--municipality`: ID de Municipio (requerido para tarifas industriales).
- `--division`: ID de División (requerido para tarifas industriales).
- `--no-cache`: Desactivar el almacenamiento en caché de los resultados.

Uso como Librería
~~~~~~~~~~~~~~~~~

También puedes utilizar la librería directamente en tu código Python:

.. code-block:: python

    from cferates import Rate, get_rates_for

    # Doméstico
    rates = get_rates_for(Rate.ONE, 2023, 1)
    print(rates)

    # Industrial
    rates = get_rates_for(Rate.GDMTO, 2023, 1, state=1, municipality=2, division=3)
    print(rates)
