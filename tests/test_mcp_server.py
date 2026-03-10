import datetime
import pytest
from unittest.mock import patch

from cferates import Rate
from cferates.mcp_server import (
    get_cfe_rates,
    list_cfe_rates,
    RateName,
    _RATE_ENUM_MAP,
)


class TestGetCfeRates:
    @patch("cferates.mcp_server.get_rates_for")
    def test_domestic_rate_1(self, mock_get_rates):
        mock_get_rates.return_value = {"Basico": "0.987"}
        result = get_cfe_rates(RateName.ONE, year=2023, month=1)
        mock_get_rates.assert_called_once_with(
            Rate.ONE, 2023, 1, None, None, None, None
        )
        assert result == {"Basico": "0.987"}

    @patch("cferates.mcp_server.get_rates_for")
    def test_domestic_rate_1a_with_summer(self, mock_get_rates):
        mock_get_rates.return_value = {"Basico": "1.50"}
        result = get_cfe_rates(RateName.ONE_A, year=2023, month=6, summer_month=3)
        mock_get_rates.assert_called_once_with(
            Rate.ONE_A, 2023, 6, 3, None, None, None
        )
        assert result == {"Basico": "1.50"}

    @patch("cferates.mcp_server.get_rates_for")
    def test_industrial_rate_with_location(self, mock_get_rates):
        mock_get_rates.return_value = {"Cargo": "2.00"}
        result = get_cfe_rates(
            RateName.GDMTO, year=2023, month=1,
            state=1, municipality=2, division=3,
        )
        mock_get_rates.assert_called_once_with(
            Rate.GDMTO, 2023, 1, None, 1, 2, 3
        )
        assert result == {"Cargo": "2.00"}

    @patch("cferates.mcp_server.get_rates_for")
    def test_defaults_to_current_date(self, mock_get_rates):
        mock_get_rates.return_value = {"Basico": "1.00"}
        with patch("cferates.mcp_server.datetime") as mock_dt:
            mock_dt.date.today.return_value = datetime.date(2024, 3, 15)
            get_cfe_rates(RateName.ONE)
        mock_get_rates.assert_called_once_with(
            Rate.ONE, 2024, 3, None, None, None, None
        )

    def test_summer_rate_requires_summer_month(self):
        with pytest.raises(ValueError, match="summer_month is required"):
            get_cfe_rates(RateName.ONE_A, year=2023, month=6)

    def test_industrial_rate_requires_location(self):
        with pytest.raises(ValueError, match="required for industrial"):
            get_cfe_rates(RateName.GDMTO, year=2023, month=1)

    def test_invalid_month(self):
        with pytest.raises(ValueError, match="month must be between"):
            get_cfe_rates(RateName.ONE, year=2023, month=13)

    def test_invalid_year_too_old(self):
        with pytest.raises(ValueError, match="year must be between"):
            get_cfe_rates(RateName.ONE, year=2017, month=1)

    def test_invalid_summer_month(self):
        with pytest.raises(ValueError, match="summer_month must be between"):
            get_cfe_rates(RateName.ONE_A, year=2023, month=6, summer_month=7)


class TestListCfeRates:
    def test_returns_domestic_and_industrial(self):
        result = list_cfe_rates()
        assert "domestic" in result
        assert "industrial" in result

    def test_domestic_rates(self):
        domestic = list_cfe_rates()["domestic"]
        for name in ("1", "1A", "1B", "1C", "1D", "1E", "1F", "DAC"):
            assert name in domestic

    def test_industrial_rates(self):
        industrial = list_cfe_rates()["industrial"]
        for name in ("GDMTO", "RAMT", "APMT", "GDMTH", "DIST", "DIT"):
            assert name in industrial

    def test_no_overlap(self):
        result = list_cfe_rates()
        assert not set(result["domestic"]) & set(result["industrial"])


class TestRateEnumMap:
    def test_all_rate_names_mapped(self):
        for name in RateName:
            assert name in _RATE_ENUM_MAP
