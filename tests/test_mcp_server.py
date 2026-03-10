import datetime
import json
from unittest.mock import patch

import pytest

from cferates.mcp_server import list_rates, get_rates, _rate_mapping, _validate_parameters


class TestListRates:
    def test_returns_valid_json(self):
        result = json.loads(list_rates())
        assert "domestic" in result
        assert "industrial" in result
        assert "notes" in result

    def test_domestic_rates_structure(self):
        result = json.loads(list_rates())
        assert result["domestic"]["simple"] == ["1", "DAC"]
        assert result["domestic"]["with_summer"] == ["1A", "1B", "1C", "1D", "1E", "1F"]

    def test_all_listed_rates_are_in_rate_mapping(self):
        result = json.loads(list_rates())
        all_rates = (
            result["domestic"]["simple"]
            + result["domestic"]["with_summer"]
            + result["industrial"]
        )
        for rate in all_rates:
            assert rate in _rate_mapping, f"Rate {rate} listed but not in _rate_mapping"


class TestGetRatesValidation:
    def test_unknown_rate(self):
        result = json.loads(get_rates("INVALID"))
        assert "error" in result
        assert "Unknown rate" in result["error"]

    def test_summer_rate_requires_summer_month(self):
        result = json.loads(get_rates("1A", year=2023, month=1))
        assert "error" in result
        assert "summer_month" in result["error"]

    def test_industrial_rate_requires_location(self):
        result = json.loads(get_rates("GDMTO", year=2023, month=1))
        assert "error" in result
        assert "state, municipality, and division" in result["error"]

    def test_industrial_rate_missing_municipality(self):
        result = json.loads(get_rates("GDMTO", year=2023, month=1, state=1, division=3))
        assert "error" in result
        assert "state, municipality, and division" in result["error"]

    def test_year_too_old(self):
        result = json.loads(get_rates("1", year=2017, month=1))
        assert "error" in result
        assert "Invalid year" in result["error"]

    def test_year_in_future(self):
        future_year = datetime.date.today().year + 1
        result = json.loads(get_rates("1", year=future_year, month=1))
        assert "error" in result
        assert "Invalid year" in result["error"]

    def test_month_too_far_in_future(self):
        fake_today = datetime.date(2023, 6, 15)
        with patch("cferates.mcp_server.datetime") as mock_dt:
            mock_dt.date.today.return_value = fake_today
            result = json.loads(get_rates("1", year=2023, month=8))
            assert "error" in result
            assert "Invalid month" in result["error"]

    def test_invalid_month_value(self):
        result = json.loads(get_rates("1", year=2023, month=13))
        assert "error" in result
        assert "Invalid month" in result["error"]

    def test_invalid_summer_month(self):
        result = json.loads(get_rates("1A", year=2023, month=6, summer_month=7))
        assert "error" in result
        assert "Invalid summer_month" in result["error"]

    def test_summer_month_not_relevant_for_rate_1(self):
        result = json.loads(get_rates("1", year=2023, month=6, summer_month=3))
        assert "error" in result
        assert "not relevant" in result["error"]

    def test_summer_month_not_relevant_for_dac(self):
        result = json.loads(get_rates("DAC", year=2023, month=6, summer_month=3))
        assert "error" in result
        assert "not relevant" in result["error"]


class TestGetRatesSuccess:
    @patch("cferates.mcp_server.get_rates_for")
    def test_domestic_rate(self, mock_get_rates_for):
        mock_get_rates_for.return_value = {"Basico": "1.23"}
        result = json.loads(get_rates("1", year=2023, month=1))
        assert result == {"Basico": "1.23"}
        mock_get_rates_for.assert_called_once()

    @patch("cferates.mcp_server.get_rates_for")
    def test_industrial_rate(self, mock_get_rates_for):
        mock_get_rates_for.return_value = {"fijo": "5.00"}
        result = json.loads(get_rates("GDMTO", year=2023, month=1, state=1, municipality=2, division=3))
        assert result == {"fijo": "5.00"}
        mock_get_rates_for.assert_called_once()

    @patch("cferates.mcp_server.get_rates_for")
    def test_case_insensitive_rate(self, mock_get_rates_for):
        mock_get_rates_for.return_value = {"Basico": "1.23"}
        result = json.loads(get_rates("dac", year=2023, month=1))
        assert result == {"Basico": "1.23"}

    @patch("cferates.mcp_server.get_rates_for")
    def test_scraper_exception_returns_error(self, mock_get_rates_for):
        mock_get_rates_for.side_effect = RuntimeError("connection failed")
        result = json.loads(get_rates("1", year=2023, month=1))
        assert "error" in result
        assert "connection failed" in result["error"]

    @patch("cferates.mcp_server.get_rates_for")
    def test_defaults_to_current_year_and_month(self, mock_get_rates_for):
        mock_get_rates_for.return_value = {}
        fake_today = datetime.date(2023, 6, 15)
        with patch("cferates.mcp_server.datetime") as mock_dt:
            mock_dt.date.today.return_value = fake_today
            get_rates("1")
            call_args = mock_get_rates_for.call_args
            assert call_args[0][1] == 2023  # year
            assert call_args[0][2] == 6     # month


class TestRateMapping:
    def test_all_domestic_rates_present(self):
        for name in ("1", "1A", "1B", "1C", "1D", "1E", "1F", "DAC"):
            assert name in _rate_mapping

    def test_all_industrial_rates_present(self):
        for name in ("GDMTO", "RAMT", "APMT", "GDMTH", "DIST", "DIT"):
            assert name in _rate_mapping

    def test_no_unsupported_rates(self):
        """Rates without scrapers should not be in _rate_mapping."""
        for name in ("PDBT", "GDBT", "APBT", "RABT"):
            assert name not in _rate_mapping


class TestValidateParameters:
    def test_valid_domestic(self):
        assert _validate_parameters("1", 2023, 6, None) is None

    def test_valid_summer(self):
        assert _validate_parameters("1A", 2023, 6, 3) is None

    def test_year_too_low(self):
        assert _validate_parameters("1", 2017, 1, None) is not None

    def test_month_zero(self):
        assert _validate_parameters("1", 2023, 0, None) is not None

    def test_month_thirteen(self):
        assert _validate_parameters("1", 2023, 13, None) is not None
