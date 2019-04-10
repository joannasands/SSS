class DataStore(object):
    def set(path, data):
        raise NotImplementedError()

    def get(path):
        raise NotImplementedError()


class DictionaryStor(DataStore):
    def __init__(self):
        self._d = dict()

    def set(path, data):
        self._d[path] = data

    def get(path):
        return self._d[path]
