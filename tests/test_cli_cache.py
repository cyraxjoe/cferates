import json
import pytest
from cferates._cli_cache import Cache


@pytest.fixture
def cache(tmp_path):
    return Cache(tmp_path)


class TestCacheContains:
    def test_contains_returns_true_for_existing_key(self, cache):
        cache[(2023, 1, None, "1")] = {"Basico": "1.23", "Intermedio": "4.56"}
        assert (2023, 1, None, "1") in cache

    def test_contains_returns_false_for_missing_key(self, cache):
        assert (2023, 1, None, "1") not in cache

    def test_contains_returns_bool_not_value(self, cache):
        cache[(2023, 1, None, "1")] = {"Basico": "1.23"}
        result = cache.__contains__((2023, 1, None, "1"))
        assert result is True
        assert type(result) is bool


class TestCacheGetItem:
    def test_getitem_returns_stored_value(self, cache):
        cache[(2023, 6, 3, "1A")] = {"Basico": "0.88", "Intermedio": "1.10"}
        result = cache[(2023, 6, 3, "1A")]
        assert result == {"Basico": "0.88", "Intermedio": "1.10"}

    def test_getitem_raises_keyerror_for_missing(self, cache):
        with pytest.raises(KeyError):
            cache[(2023, 1, None, "1")]

    def test_getitem_with_variable_length_key(self, cache):
        # Industrial rates have 7-part keys
        key = (2023, 1, None, "GDMTO", 1, 2, 3)
        cache[key] = {"fijo": "10.0", "variable": "1.5"}
        assert cache[key] == {"fijo": "10.0", "variable": "1.5"}


class TestCacheSetItem:
    def test_setitem_creates_nested_structure(self, cache):
        cache[(2023, 1, None, "1")] = {"Basico": "1.23"}
        assert cache.content["2023"]["1"]["None"]["1"] == {"Basico": "1.23"}

    def test_setitem_persists_to_disk(self, tmp_path):
        cache = Cache(tmp_path)
        cache[(2023, 1, None, "1")] = {"Basico": "1.23"}
        # Re-read from disk
        cache2 = Cache(tmp_path)
        assert (2023, 1, None, "1") in cache2

    def test_setitem_converts_values_to_strings(self, cache):
        cache[(2023, 1, None, "1")] = {"Basico": 1.23, "Intermedio": 4.56}
        result = cache[(2023, 1, None, "1")]
        assert result == {"Basico": "1.23", "Intermedio": "4.56"}


class TestCacheDelItem:
    def test_delitem_removes_entry(self, cache):
        cache[(2023, 1, None, "1")] = {"Basico": "1.23"}
        del cache[(2023, 1, None, "1")]
        assert (2023, 1, None, "1") not in cache

    def test_delitem_raises_keyerror_for_missing(self, cache):
        with pytest.raises(KeyError):
            del cache[(2023, 1, None, "1")]

    def test_delitem_persists_to_disk(self, tmp_path):
        cache = Cache(tmp_path)
        cache[(2023, 1, None, "1")] = {"Basico": "1.23"}
        del cache[(2023, 1, None, "1")]
        cache2 = Cache(tmp_path)
        assert (2023, 1, None, "1") not in cache2


class TestCacheInit:
    def test_creates_cache_file_if_missing(self, tmp_path):
        cache_path = tmp_path / "cache.json"
        assert not cache_path.exists()
        Cache(tmp_path)
        assert cache_path.exists()
        with open(cache_path) as f:
            assert json.load(f) == {}

    def test_loads_existing_cache_file(self, tmp_path):
        cache_path = tmp_path / "cache.json"
        data = {"2023": {"1": {"None": {"1": {"Basico": "1.23"}}}}}
        with open(cache_path, "w") as f:
            json.dump(data, f)
        cache = Cache(tmp_path)
        assert (2023, 1, None, "1") in cache
