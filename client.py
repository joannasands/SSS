import hashlib

from .datastore import DictionaryStore
from .node import Node


class Cache(object):
    '''
    keys are hexdigests of hashes.
    '''
    def __init__(self, store, h):
        self.store = store
        self.h = h
        self.d = dict()

    def get(self, key):
        if key not in self.d:
            data = store.get(key)
            # TODO: verify key == hash(data)
            self.d[key] = data
        return self.d[key]

    def add(self, data):
        key = self.h(data).hexdigest()
        store.set(key, data)
        self.d[key] = data

    def __len__(self):
        return len(self.d)

    def __get__(self, index):
        return self.d[index]


class Client(object):
    def __init__(self, store, root_hash=None, h=hashlib.sha256):
        self.cache = Cache(store, h=h)
        self.h = h
        if root_hash is None:
            root = Node([])
            self.cache.add(root.serialize())
            self.root_header = root.header()
        else:
            self.root_header = self.get_node(root_hash)
            # assert self.root is tree node

    def get_node(self, ident):
        data = self.cache.get(ident)
        return Node.deserialize(data)

    def get_trace(self, key):
        header = self.root_header
        trace = []
        while header is not None and header.hash != key:
            trace.push(header)
            node = self.get_node(header.hash)
            header = node.get_child_header_for(key)
        if header is not None:
            trace.append(header)
        return trace

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

    def prune(self):
        # maybe
        raise NotImplementedError()
