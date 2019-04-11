import hashlib

from .datastore import DictionaryStore
from .node import Node


class Cache(object):
    def __init__(self, store):
        self.store = store
        self.d = dict()

    def get(self, key):
        if key not in self.d:
            self.d[key] = store.get(key)
        return self.d[key]


class Client(object):
    def __init__(self, store, root_hash=None, h=hashlib.sha256):
        self.cache = Cache(store)
        self.h = h
        if root_hash is None:
            self.root = Node([])
        else:
            self.root = self.get_node(root_hash)

    def get_node(self, ident):
        data = self.cache.get(ident)
        return Node.deserialize(data)

    def add(self, path, data):
        raise NotImplementedError()

    def remove(self, path):
        raise NotImplementedError()

    def edit(self, path, data):
        raise NotImplementedError()

    def verify(self, path, data):
        raise NotImplementedError()

    def ls(self, path):
        raise NotImplementedError()

    def download_and_verify(self, path):
        raise NotImplementedError()

    def prune_cache(self):
        # maybe
        raise NotImplementedError()
