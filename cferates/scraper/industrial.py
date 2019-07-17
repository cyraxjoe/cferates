import time
import random
import datetime

from cferates import Rate
from cferates.scraper.base import (
    AbstractStatefulScraper,
    AbstractForm,
    HiddenField,
    SelectField
)


class IndustiralRateForm(AbstractForm):
    hdAnio = HiddenField("ctl00$ContentPlaceHolder1$hdAnio")
    hdMes = HiddenField("ctl00$ContentPlaceHolder1$hdMes")
    fecha_ddAnio = SelectField("ctl00$ContentPlaceHolder1$Fecha$ddAnio")
    mes = SelectField("ctl00$ContentPlaceHolder1$Fecha2$ddMes")
    estado = SelectField("ctl00$ContentPlaceHolder1$EdoMpoDiv$ddEstado")
    municipio = SelectField("ctl00$ContentPlaceHolder1$EdoMpoDiv$ddMunicipio")
    division = SelectField("ctl00$ContentPlaceHolder1$EdoMpoDiv$ddDivision")

    @property
    def anio(self):
        raise NotImplementedError("This property is not meant to be used.")

    @anio.setter
    def anio(self, anio):
        """
        Helper property setter to configure the apparently, always equal
        hidden and select year fields.
        """
        self.hdAnio = anio
        self.fecha_ddAnio = anio


class BaseIndustrialScraper(AbstractStatefulScraper):
    rate: Rate = None
    FormCls = IndustiralRateForm

    @staticmethod
    def delay():
        # sleep between 0.1 < 0.2 seconds
        time.sleep(random.randrange(10, 20) / 100.)

    def _select_year(self, year):
        self.form.anio = year
        params = self.form(IndustiralRateForm.fecha_ddAnio)
        return self.http_post_request(params)

    def _select_month(self, month):
        self.form.mes = month
        params = self.form(IndustiralRateForm.mes)
        return self.http_post_request(params)

    def _select_state(self, state):
        self.form.estado = state
        params = self.form(IndustiralRateForm.estado)
        return self.http_post_request(params)

    def _select_mun(self, mun):
        self.form.municipio = mun
        params = self.form(IndustiralRateForm.municipio)
        return self.http_post_request(params)

    def _select_div(self, div):
        self.form.division = div
        params = self.form(IndustiralRateForm.division)
        return self.http_post_request(params)

    def request(self, year, month, state, mun, div):
        assert 0 < month < 13
        assert 0 < state < 33
        if year < 2019:
            # because 2018 and older, has other field names and most likely is irrelevant
            raise Exception("Currently this class only support the scaping of 2019 and up.")
        if year != datetime.date.today().year:
            self._select_year(year)
            self.delay()
        self._select_month(month)
        self.delay()
        self._select_state(state)
        self.delay()
        self._select_mun(mun)
        self.delay()
        soup = self._select_div(div)
        return self._scrape_values(soup)

    def _scrape_values(self, soup):
        raise NotImplementedError(
            f"The class { self.__class__ } is not fully defined")

class OrdinaryIndustrialScraper(BaseIndustrialScraper):
    scrape_capacity: bool  = True

    def _scrape_values(self, soup):
        # $/mes
        fijo = soup.select_one(
            "table.table tr:nth-child(2) td:last-child").text.strip()
        # $/kWh
        variable = soup.select_one(
            "table.table tr:nth-child(3) td:last-child").text.strip()
        # $/kW
        distribucion = soup.select_one(
            "table.table tr:nth-child(4) td:last-child").text.strip()
        values  = {
            "fijo": fijo,
            "variable": variable,
            "distribucion": distribucion
        }
        if self.scrape_capacity:
            # $/kW
            capacidad = soup.select_one(
                "table.table tr:nth-child(5) td:last-child").text.strip()
            values["capacidad"] = capacidad
        return values


class ScheduledIndustrialScraper(BaseIndustrialScraper):
    @property
    def row_map(self):
        raise NotImplementedError(f"The class is { self.__class__ }not fully implemented")

    def _scrape_values(self, soup):
        main_table = soup.select_one("table.table")
        value_from_row = (lambda row_num: main_table.select_one(
            f"tr:nth-child({ row_num }) td:last-child").text.strip())
        return {
            name: value_from_row(num)
            for num, name in self.row_map.items()
        }

class IndustrialScraper_Rate_GDMTO(OrdinaryIndustrialScraper):
    rate = Rate.GDMTO
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCREIndustria/Tarifas/GranDemandaMTO.aspx"

class IndustrialScraper_Rate_RAMT(OrdinaryIndustrialScraper):
    rate = Rate.RAMT
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCREIndustria/Tarifas/RiegoAgricolaMT.aspx"

class IndustrialScraper_Rate_APMT(OrdinaryIndustrialScraper):
    rate = Rate.APMT
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCREIndustria/Tarifas/AlumbradoPublicoMT.aspx"
    scrape_capacity = False


class IndustrialScraper_Rate_GDMTH(ScheduledIndustrialScraper):
    rate = Rate.GDMTH
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCREIndustria/Tarifas/GranDemandaMTH.aspx"
    row_map = {
        2: "fijo",
        3: "base",
        4: "intermedia",
        5: "punta",
        6: "distribucion",
        7: "capacidad",
    }


class IndustrialScraper_Rate_DIST(ScheduledIndustrialScraper):
    rate = Rate.DIST
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCREIndustria/Tarifas/DemandaIndustrialSub.aspx"
    row_map = {
        2: "fijo",
        3: "base",
        4: "intermedia",
        5: "punta",
        6: "semipunta",
        7: "capacidad",
    }


class IndustrialScraper_Rate_DIT(ScheduledIndustrialScraper):
    # basically the same as DIST
    rate = Rate.DIT
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCREIndustria/Tarifas/DemandaIndustrialTran.aspx"
    row_map = {
        2: "fijo",
        3: "base",
        4: "intermedia",
        5: "punta",
        6: "semipunta",
        7: "capacidad",
    }
