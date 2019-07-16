from decimal import Decimal

from cferates import Rate
from cferates.scraper.base import AbstractStatefulScraper


class BaseDomesticScraper(AbstractStatefulScraper):
    rate: Rate = None

    def __init__(self, do_initial_request=True, prev_session=None):
        super().__init__(do_initial_request, prev_session)
        self.form_fields = {
            "hidden-anio": "ctl00$ContentPlaceHolder1$hdAnio",
            "anio": "ctl00$ContentPlaceHolder1$Fecha$ddAnio",
        }

    def _scrape_values(self, soup, two_intermediates):
        main_table = soup.select("table.table")
        if not main_table:
            raise Exception(
                "The main table is missing, verify that the "
                "css selector 'table.table' is still valid")
        main_table = main_table.pop()
        rows = main_table.find_all('td')
        # start with the always present, basic
        values = [
            # basic
            rows[1].text.strip(),
            # intermediate (low?)
            rows[4].text.strip(),
            # intermediate high or excess
            rows[7].text.strip()
        ]
        if two_intermediates:
            keys = ("Basico", "IntermedioBajo", "IntermedioAlto", "Excedente")
            # in this case, this is excess
            values.append(rows[10].text.strip())
        else:
            keys = ("Basico", "Intermedio", "Excedente")
        if all(values):
            return dict(zip(keys, map(Decimal, values)))
        else:
            raise Exception(
                "Unable to obtain all the values: \n {}".format(values))



class BaseDomesticScraperWithSummer(BaseDomesticScraper):
    def __init__(self, do_initial_request=True, prev_session=None):
        super().__init__(do_initial_request, prev_session)
        assert self.rate != Rate.ONE
        extra_fields = {
           # month field from 1 ... 12, 0 is not set
            "mes-verano": "ctl00$ContentPlaceHolder1$MesVerano1$ddMesVerano",
            # month field from 1 ... 12, 0 is not set
            "mes-consulta": "ctl00$ContentPlaceHolder1$MesVerano2$ddMesConsulta"
        }
        self.form_fields.update(extra_fields)

    def _has_two_intermediates(self, month, summer_month):
        if self.rate in (Rate.ONE_A, Rate.ONE_B):
            # only 1C and up has two intermediates in summer
            return False
        elif month < summer_month or month > (summer_month + 5):
            # the summer is considered 6 months from the starting
            # month of summer, this is outsude of summer, hence
            # don't have two intermediates
            return False
        else:
            # this is summer and on a rate 1C and up
            return  True

    def request(self, year: int, month: int, summer_month: int):
        # summer month has to be between Feb - May
        if summer_month < 2 or summer_month > 5:
            raise Exception(
                "Invalid summer month {} is not between Feb - May".format(summer_month))
        str_year, str_month, str_summer_month = map(str, (year, month, summer_month))
        fields = {
            self.form_fields["hidden-anio"]: str_year,
            self.form_fields["anio"]: str_year,
            self.form_fields["mes-verano"]: str_summer_month,
            self.form_fields["mes-consulta"]: str_month
        }
        target = self.form_fields["mes-consulta"]
        params = self._get_request_params(target, **fields)
        soup = self._make_stateful_request('POST', data=params)
        two_intermediates = self._has_two_intermediates(month, summer_month)
        return self._scrape_values(soup, two_intermediates)


class DomesticScraper_Rate_1(BaseDomesticScraper):
    rate = Rate.ONE
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1.aspx"

    def __init__(self, do_initial_request=True, prev_session=None):
        super().__init__(do_initial_request, prev_session)
        extra_fields = {
            # month field from 1 ... 12, 0 is not set
            "mes-consulta": "ctl00$ContentPlaceHolder1$MesVerano1$ddMesConsulta"
        }
        self.form_fields.update(extra_fields)

    def request(self, year: int, month: int):
        str_year, str_month = map(str, (year, month))
        fields = {
            self.form_fields["hidden-anio"]: str_year,
            self.form_fields["anio"]: str_year,
            self.form_fields["mes-consulta"]: str_month
        }
        target = self.form_fields["mes-consulta"]
        params = self._get_request_params(target, **fields)
        soup = self._make_stateful_request('POST', data=params)
        return self._scrape_values(soup, two_intermediates=False)


class DomesticScraper_Rate_1A(BaseDomesticScraperWithSummer):
    rate = Rate.ONE_A
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1A.aspx"

class DomesticScraper_Rate_1B(BaseDomesticScraperWithSummer):
    rate = Rate.ONE_B
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1B.aspx"

class DomesticScraper_Rate_1C(BaseDomesticScraperWithSummer):
    rate = Rate.ONE_C
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1C.aspx"

class DomesticScraper_Rate_1D(BaseDomesticScraperWithSummer):
    rate = Rate.ONE_D
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1D.aspx"

class DomesticScraper_Rate_1E(BaseDomesticScraperWithSummer):
    rate = Rate.ONE_E
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1E.aspx"

class DomesticScraper_Rate_1F(BaseDomesticScraperWithSummer):
    rate = Rate.ONE_F
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1F.aspx"


class DomesticScraper_Rate_DAC(AbstractStatefulScraper):
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/TarifaDAC.aspx"

    def __init__(self, do_initial_request=True, prev_session=None):
        super().__init__(do_initial_request, prev_session)
        self.form_fields = {
            "hidden-anio": "ctl00$ContentPlaceHolder1$hdAnio",
            # most likely, the previous  year
            "hidden-mes": "ctl00$ContentPlaceHolder1$hdMes",
            "anio": "ctl00$ContentPlaceHolder1$Fecha$ddAnio",
            # this is relevant in case we want tu support prev 2019 dates
            #"mes-consulta": "ctl00$ContentPlaceHolder1$MesVerano3$ddMesConsulta",
            ##
            # month field from 1 ... 12, 0 is not set,
            # used for 2019 (and maybe up?)
            "mes-consulta-new": "ctl00$ContentPlaceHolder1$Fecha1$ddMes"
        }

    def request(self, year: int, month: int):
        if year < 2019:
            raise Exception("Currently this class only support the scaping of 2019 and up for DAC")
        str_year = str(year)
        str_month = str(month)
        fields = {
            self.form_fields["hidden-anio"]: str_year,
            self.form_fields["anio"]: str_year,
            # explicit 0, to specify a clean request (no previous month)
            self.form_fields["hidden-mes"]: "0",
            self.form_fields["mes-consulta-new"]: str_month
        }
        target = self.form_fields["mes-consulta-new"]
        params = self._get_request_params(target, **fields)
        return self._make_stateful_request('POST', data=params)


    def _scrape_values(self, soup):
        dac_fv_table = soup.select("#TarifaDacFV")
        dac_v_table = soup.select("#TarifaDacV")
        if not dac_fv_table:
            raise Exception("The selector for the DAC FV table is not working.")
        if not dac_v_table:
            raise Exception("The selector for the DAC V table is not working.")
        dac_fv_table = dac_fv_table.pop()
        dac_v_table = dac_v_table.pop()

        rows = main_table.find_all('td')
        # start with the always present, basic
        values = [
            # basic
            rows[1].text.strip(),
            # intermediate (low?)
            rows[4].text.strip(),
            # intermediate high or excess
            rows[7].text.strip()
        ]
        if two_intermediates:
            keys = ("Basico", "IntermedioBajo", "IntermedioAlto", "Excedente")
            # in this case, this is excess
            values.append(rows[10].text.strip())
        else:
            keys = ("Basico", "Intermedio", "Excedente")
        if all(values):
            return dict(zip(keys, map(Decimal, values)))
        else:
            raise Exception(
                "Unable to obtain all the values: \n {}".format(values))
