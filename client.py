import bisect
import hashlib
import os

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
            if self.h(data).hexdigest() != key:
                raise ValueError()
            self.d[key] = data
        return self.d[key]

    def add(self, data):
        key = self.h(data).hexdigest()
        store.set(key, data)
        self.d[key] = data
        return key

    def __len__(self):
        return len(self.d)

    def __get__(self, index):
        return self.d[index]


class Client(object):
    def __init__(self, store, root_hash=None, h=hashlib.sha256, b=100):
        '''
        store: data store
        root_hash: hex encoding of merkle root
        h: hashing algorithm
        b: max node size
        '''
        self.cache = Cache(store, h=h)
        self.h = h
        self.b = b
        if root_hash is None:
            root = self.create_node([])
        else:
            root = self.get_node(root_hash)
        root_header = root.header()
        if root_header.is_leaf:
            raise ValueError()
        self.root_hash = root_header.subtree_hash

    def get_node(self, node_hash):
        data = self.cache.get(node_hash)
        return Node.deserialize(data)

    def create_node(self, headers):
        node = Node(headers)
        self.cache.add(node.serialize())
        return node

    def hash_path(self, path):
        abs_path = os.path.normpath(os.join('/', path)).encode('utf-8')
        return self.h(abs_path).hexdigest()

    def get_trace(self, key):
        header = self.get_node(self.root_hash).header()
        trace = []
        while header is not None and not header.is_leaf:
            trace.push(header)
            node = self.get_node(header.subtree_hash)
            if node is not None:
                header = node.get_child_header_for(key)
                if header is None and node.children:
                    header = node.children[-1]
            else:
                header = None
        if header is not None:
            trace.append(header)
        return trace

    def add(self, path, data):
        key = self.hash_path(path)
        value = self.cache.add(data)
        trace = self.get_trace(key)
        leaf = trace[-1]
        if leaf.is_leaf:
            if leaf.key_upperbound == key:
                # overwrite?
                raise ValueError()
            else:
                trace.pop()
        node = self.get_node(header.subtree_hash)
        headers_to_remove = []
        headers_to_add = [Node.make_header(subtree_hash=value, is_leaf=True, key=key)]
        while trace:
            node = self.get_node(trace.pop().subtree_hash)
            headers = list(node.children)
            while headers_to_remove:
                headers.remove(headers_to_remove.pop())
            while headers_to_add:
                bisect.insort(headers, headers_to_add.pop())
            if len(node) >= b:
                left_node = self.create_node(headers[:b//2])
                right_node = self.create_node(headers[b//2:])
                headers_to_add = [left_node.header(), right_node.header()]
            else:
                _node = create_node(headers)
                headers_to_add = [_node.header()]
            headers_to_remove = [node.header()]
        if len(headers_to_add) > 1:
            node = self.create_node(headers_to_add)
        return node.header()

    def remove(self, path):
        raise NotImplementedError()

    def edit(self, path, data):
        raise NotImplementedError()

    def verify(self, path, data):
        raise NotImplementedError()

    def ls(self, path):
        raise NotImplementedError()

    def download(self, path):
        key = self.hash_path(path)
        trace = self.get_trace(key)
        header = trace[-1]
        if not header.is_leaf or header.key_upperbound == key:
            raise KeyError()
        data = self.cache.get(header.subtree_hash)
        return data

    def prune(self):
        # maybe
        raise NotImplementedError()
