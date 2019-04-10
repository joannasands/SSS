class DataStore(object):
    def get(self, path):
        return self.get(path)

    def set(self, path, data):
        return self.set(path, data)

    def _get(self, path):
        raise NotImplementedError()

    def _set(self, path, data):
        raise NotImplementedError()


class DictionaryStore(DataStore):
    def __init__(self):
        self._d = dict()

    def _get(self, path):
        return self._d[path]

    def _set(self, path, data):
        self._d[path] = data
