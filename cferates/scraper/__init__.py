from cferates import Rate
from cferates.scraper.domestic  import (
    DomesticScraper_Rate_1,
    DomesticScraper_Rate_1A,
    DomesticScraper_Rate_1B,
    DomesticScraper_Rate_1C,
    DomesticScraper_Rate_1D,
    DomesticScraper_Rate_1E,
    DomesticScraper_Rate_1F,
    DomesticScraper_Rate_DAC
)
from cferates.scraper.industrial import (
    IndustrialScraper_Rate_GDMTO,
    IndustrialScraper_Rate_RAMT,
    IndustrialScraper_Rate_APMT,
    IndustrialScraper_Rate_GDMTH,
    IndustrialScraper_Rate_DIST,
    IndustrialScraper_Rate_DIT
)


SCRAPER_MAP = {
    Rate.ONE: DomesticScraper_Rate_1,
    Rate.ONE_A: DomesticScraper_Rate_1A,
    Rate.ONE_B: DomesticScraper_Rate_1B,
    Rate.ONE_C: DomesticScraper_Rate_1C,
    Rate.ONE_D: DomesticScraper_Rate_1D,
    Rate.ONE_E: DomesticScraper_Rate_1E,
    Rate.ONE_F: DomesticScraper_Rate_1F,
    Rate.DAC: DomesticScraper_Rate_DAC,
    Rate.GDMTO: IndustrialScraper_Rate_GDMTO,
    Rate.RAMT: IndustrialScraper_Rate_RAMT,
    Rate.APMT: IndustrialScraper_Rate_APMT,
    Rate.GDMTH: IndustrialScraper_Rate_GDMTH,
    Rate.DIST: IndustrialScraper_Rate_DIST,
    Rate.DIT: IndustrialScraper_Rate_DIT
}



def get_rates_for(rate: Rate, year: int, month: int, summer_month: int = None,
                  state: int = None, municipality: int = None, division: int = None):
    """
    Helper function to request the rates without reusing any "requests" session.

    DO NOT use this function if you're planning to make a lot of requests, better
    to reuse the session to make it look more natural (header/session wise).
    """
    scraper = SCRAPER_MAP[rate]
    if rate in (Rate.ONE, Rate.DAC):
        return scraper().request(year, month)
    elif rate in (Rate.ONE_A, Rate.ONE_B, Rate.ONE_C, Rate.ONE_D, Rate.ONE_E, Rate.ONE_F):
        if summer_month is None:
            raise TypeError("The argument `summer_month` is required for rates 1A - 1F")
        return scraper().request(year, month, summer_month)
    else:
        # Industrial rates
        if any(arg is None for arg in (state, municipality, division)):
            raise TypeError("The arguments `state`, `municipality` and `division` are required for industrial rates")
        return scraper().request(year, month, state, municipality, division)
