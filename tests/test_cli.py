import datetime
import pytest
import click
from unittest.mock import patch

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
        """Use a fixed past date to ensure the test always exercises the check."""
        # 2023-06-15: month 8 is 2 ahead of June, should be rejected
        fake_today = datetime.date(2023, 6, 15)
        with patch("cferates.cli.datetime") as mock_dt:
            mock_dt.date.today.return_value = fake_today
            with pytest.raises(click.BadOptionUsage, match="Invalid month"):
                _verify_parameters(2023, 8, None, "1", None, None, None)


class _StubCache:
    """Simple stub replacing Cache to avoid MagicMock dunder-method issues."""

    def __init__(self, data=None):
        self._data = data or {}

    def __contains__(self, key):
        return key in self._data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value


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
        mock_cache_cls.return_value = _StubCache()
        mock_get_rates.return_value = {"Basico": "1.23"}

        result = get_rates(2023, 1, None, False, "1", None, None, None)
        mock_get_rates.assert_called_once()
        assert result == {"Basico": "1.23"}

    @patch("cferates.cli.Cache")
    @patch("cferates.cli._ensure_app_dir")
    @patch("cferates.cli.get_rates_for")
    def test_cache_hit_returns_cached(self, mock_get_rates, mock_app_dir, mock_cache_cls):
        mock_app_dir.return_value = "/fake"
        key = (2023, 1, None, "1", None, None, None)
        mock_cache_cls.return_value = _StubCache({key: {"Basico": "1.23"}})

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
