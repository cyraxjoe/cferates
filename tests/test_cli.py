import datetime
import pytest
import click
from unittest.mock import patch, MagicMock

from cferates.cli import _verify_parameters, get_rates, _rate_mapping


class TestVerifyParameters:
    def test_domestic_rate_1_valid(self):
        _verify_parameters(2023, 1, None, "1", None, None, None)

    def test_domestic_rate_1a_valid(self):
        _verify_parameters(2023, 6, 3, "1A", None, None, None)

    def test_domestic_rate_1_rejects_summer_month(self):
        with pytest.raises(click.BadOptionUsage, match="not relevant"):
            _verify_parameters(2023, 6, 3, "1", None, None, None)

    def test_dac_rejects_summer_month(self):
        with pytest.raises(click.BadOptionUsage, match="not relevant"):
            _verify_parameters(2023, 6, 3, "DAC", None, None, None)

    def test_industrial_rate_requires_state(self):
        with pytest.raises(click.UsageError, match="required for industrial"):
            _verify_parameters(2023, 1, None, "GDMTO", None, 2, 3)

    def test_industrial_rate_requires_municipality(self):
        with pytest.raises(click.UsageError, match="required for industrial"):
            _verify_parameters(2023, 1, None, "GDMTO", 1, None, 3)

    def test_industrial_rate_requires_division(self):
        with pytest.raises(click.UsageError, match="required for industrial"):
            _verify_parameters(2023, 1, None, "GDMTO", 1, 2, None)

    def test_industrial_rate_valid(self):
        _verify_parameters(2023, 1, None, "GDMTO", 1, 2, 3)

    def test_industrial_rate_accepts_zero_values(self):
        """Regression test: all() treated 0 as falsy, rejecting valid IDs."""
        _verify_parameters(2023, 1, None, "GDMTO", 0, 2, 3)

    def test_year_too_old(self):
        with pytest.raises(click.BadOptionUsage, match="Invalid year"):
            _verify_parameters(2017, 1, None, "1", None, None, None)

    def test_year_in_future(self):
        future_year = datetime.date.today().year + 1
        with pytest.raises(click.BadOptionUsage, match="Invalid year"):
            _verify_parameters(future_year, 1, None, "1", None, None, None)

    def test_month_too_far_in_future(self):
        today = datetime.date.today()
        # A month that is more than 1 ahead of the current month
        far_month = today.month + 2
        if far_month <= 12:
            with pytest.raises(click.BadOptionUsage, match="Invalid month"):
                _verify_parameters(today.year, far_month, None, "1", None, None, None)


class TestGetRates:
    @patch("cferates.cli.get_rates_for")
    def test_no_cache_calls_get_rates_for(self, mock_get_rates):
        mock_get_rates.return_value = {"Basico": "1.23"}
        result = get_rates(2023, 1, None, True, "1", None, None, None)
        mock_get_rates.assert_called_once_with(
            _rate_mapping["1"], 2023, 1, None, None, None, None
        )
        assert result == {"Basico": "1.23"}

    @patch("cferates.cli.Cache")
    @patch("cferates.cli._ensure_app_dir")
    @patch("cferates.cli.get_rates_for")
    def test_cache_miss_fetches_and_stores(self, mock_get_rates, mock_app_dir, mock_cache_cls):
        mock_app_dir.return_value = "/fake"
        cache_instance = MagicMock()
        cache_instance.__contains__ = MagicMock(return_value=False)
        cache_instance.__getitem__ = MagicMock(return_value={"Basico": "1.23"})
        mock_cache_cls.return_value = cache_instance
        mock_get_rates.return_value = {"Basico": "1.23"}

        result = get_rates(2023, 1, None, False, "1", None, None, None)
        mock_get_rates.assert_called_once()
        assert result == {"Basico": "1.23"}

    @patch("cferates.cli.Cache")
    @patch("cferates.cli._ensure_app_dir")
    @patch("cferates.cli.get_rates_for")
    def test_cache_hit_returns_cached(self, mock_get_rates, mock_app_dir, mock_cache_cls):
        mock_app_dir.return_value = "/fake"
        cache_instance = MagicMock()
        cache_instance.__contains__ = MagicMock(return_value=True)
        cache_instance.__getitem__ = MagicMock(return_value={"Basico": "1.23"})
        mock_cache_cls.return_value = cache_instance

        result = get_rates(2023, 1, None, False, "1", None, None, None)
        mock_get_rates.assert_not_called()
        assert result == {"Basico": "1.23"}


class TestRateMapping:
    def test_all_domestic_rates_present(self):
        for name in ("1", "1A", "1B", "1C", "1D", "1E", "1F", "DAC"):
            assert name in _rate_mapping

    def test_all_industrial_rates_present(self):
        for name in ("GDMTO", "RAMT", "APMT", "GDMTH", "DIST", "DIT"):
            assert name in _rate_mapping
