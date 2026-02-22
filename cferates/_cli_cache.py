import json


class Cache:

    def __init__(self, app_dir):
        self.cache_path = app_dir / 'cache.json'
        if not self.cache_path.exists():
            with open(self.cache_path, "w") as cache:
                cache.write("{}\n")
        self._load_cache()

    def _load_cache(self):
        with open(self.cache_path) as cache:
            self.content = json.load(cache)

    def __contains__(self, item):
        try:
            return self[item]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, item):
        content_level = self.content
        for part in map(str, item):
            content_level = content_level[part]
        return content_level

    def __setitem__(self, key_tuple, value):
        content_level = self.content
        for part in map(str, key_tuple[:-1]):
            try:
                content_level[part]
            except KeyError:
                content_level[part] = {}
            content_level = content_level[part]
        keys = map(str, tuple(value.keys()))
        values = map(str, value.values())
        content_level[str(key_tuple[-1])] = dict(zip(keys, values))
        self.save()

    def __delitem__(self, key):
        content_level = self.content
        for part in map(str, key[:-1]):
            content_level = content_level[part]
        del content_level[str(key[-1])]
        self.save()

    def save(self):
        with open(self.cache_path, "w") as cache:
            json.dump(self.content, cache)
