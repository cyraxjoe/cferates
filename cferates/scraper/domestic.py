from cferates import Rate
from cferates.scraper.base import (
    AbstractStatefulScraper,
    AbstractStatefulField,
    AbstractForm,
    SelectField,
    HiddenField
)


class BaseDomesticRateForm(AbstractForm):
    hdAnio = HiddenField("ctl00$ContentPlaceHolder1$hdAnio")
    fecha_ddAnio = SelectField("ctl00$ContentPlaceHolder1$Fecha$ddAnio")

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


class DomesticRateOneForm(BaseDomesticRateForm):
    mes_consulta = SelectField(
        "ctl00$ContentPlaceHolder1$MesVerano1$ddMesConsulta",
        "0"
    )

class DomesticRateWithSummerForm(BaseDomesticRateForm):
    # month fields from 1 ... 12, 0 is not set
    mes_verano  = SelectField(
        "ctl00$ContentPlaceHolder1$MesVerano1$ddMesVerano",
        "0"
    )
    mes_consulta = SelectField(
        "ctl00$ContentPlaceHolder1$MesVerano2$ddMesConsulta",
        "0"
    )

class DACRateForm(BaseDomesticRateForm):
    hdMes = HiddenField("ctl00$ContentPlaceHolder1$hdMes", "0")
    mes_consulta = SelectField("ctl00$ContentPlaceHolder1$Fecha1$ddMes", "0")


class BaseDomesticScraper(AbstractStatefulScraper):
    rate: Rate = None
    FormCls = BaseDomesticRateForm

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
            return dict(zip(keys, values))
        else:
            raise Exception(
                "Unable to obtain all the values: \n {}".format(values))



class BaseDomesticScraperWithSummer(BaseDomesticScraper):
    FormCls = DomesticRateWithSummerForm

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
        self.form.anio = year
        self.form.mes_verano = summer_month
        self.form.mes_consulta = month
        params = self.form(DomesticRateWithSummerForm.mes_consulta)
        soup = self.http_post_request(params)
        two_intermediates = self._has_two_intermediates(month, summer_month)
        return self._scrape_values(soup, two_intermediates)


class DomesticScraper_Rate_1(BaseDomesticScraper):
    rate = Rate.ONE
    FormCls = DomesticRateOneForm
    main_url = "https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1.aspx"

    def request(self, year: int, month: int):
        self.form.anio = year
        self.form.mes_consulta = month
        params = self.form(target=DomesticRateOneForm.mes_consulta)
        soup = self.http_post_request(params)
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
    FormCls = DACRateForm

    @staticmethod
    def scrape_from_row(row):
        name, *values = [r.text.replace("$", "").strip() for r in row]
        return {name: values}

    def request(self, year: int, month: int):
        if year < 2019:
            raise Exception("Currently this class only support the scaping of 2019 and up for DAC")
        self.form.anio = year
        self.form.mes_consulta = month
        params = self.form(DACRateForm.mes_consulta)
        soup = self.http_post_request(params)
        return self._scrape_values(soup)

    def _scrape_values(self, soup):
        dac_fv_rows = soup.select("#TarifaDacFV td")
        dac_v_rows = soup.select("#TarifaDacV td")
        if not dac_fv_rows:
            raise Exception("The selector for the DAC FV table is not working.")
        if not dac_v_rows:
            raise Exception("The selector for the DAC V table is not working.")
        values = {}
        values.update(self.scrape_from_row(dac_fv_rows[:4]))
        values.update(self.scrape_from_row(dac_fv_rows[4:]))
        start, step = 0, 3
        for end in range(step, len(dac_v_rows) + step, step):
            values.update(self.scrape_from_row(dac_v_rows[start:end]))
            start = end
        return values
