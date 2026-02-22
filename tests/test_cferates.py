import pytest
from unittest.mock import MagicMock, patch
from cferates import Rate
from cferates.scraper import get_rates_for

@pytest.fixture
def mock_scrapers():
    with patch('cferates.scraper.SCRAPER_MAP') as mock_map:
        # Create mock scraper classes
        mocks = {}
        # We only mock a subset for testing logic
        for rate in (Rate.ONE, Rate.ONE_A, Rate.GDMTO):
            # The scraper in the map is a class, so calling it returns an instance
            scraper_cls = MagicMock()
            scraper_instance = MagicMock()
            scraper_instance.request.return_value = {"rate": "value"}
            scraper_cls.return_value = scraper_instance
            mocks[rate] = scraper_cls

        mock_map.__getitem__.side_effect = mocks.__getitem__
        yield mocks

def test_get_rates_for_domestic_1(mock_scrapers):
    result = get_rates_for(Rate.ONE, 2023, 1)
    mock_scrapers[Rate.ONE].return_value.request.assert_called_with(2023, 1)
    assert result == {"rate": "value"}

def test_get_rates_for_domestic_1a(mock_scrapers):
    result = get_rates_for(Rate.ONE_A, 2023, 1, summer_month=2)
    mock_scrapers[Rate.ONE_A].return_value.request.assert_called_with(2023, 1, 2)

def test_get_rates_for_domestic_1a_missing_summer(mock_scrapers):
    with pytest.raises(TypeError, match="rates 1A - 1F"):
        get_rates_for(Rate.ONE_A, 2023, 1)

def test_get_rates_for_industrial_gdmto(mock_scrapers):
    get_rates_for(Rate.GDMTO, 2023, 1, state=1, municipality=2, division=3)
    mock_scrapers[Rate.GDMTO].return_value.request.assert_called_with(2023, 1, 1, 2, 3)

def test_get_rates_for_industrial_missing_params(mock_scrapers):
    with pytest.raises(TypeError, match="required for industrial rates"):
        get_rates_for(Rate.GDMTO, 2023, 1)
