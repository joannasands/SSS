import bisect
import hashlib
import os
import copy

from datastore import DictionaryStore
from node import Node, Header


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
            data = self.store.get(key)
            if self.h(data).hexdigest() != key:
                raise ValueError()
            self.d[key] = data
        return self.d[key]

    def add(self, data):
        key = self.h(data).hexdigest()
        self.store.set(key, data)
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
        abs_path = os.path.normpath(os.path.join('/', path)).encode('utf-8')
        return self.h(abs_path).hexdigest()

    def get_trace(self, key):
        node = self.get_node(self.root_hash)
        header = self.get_node(self.root_hash).header()
        trace = []
        while header is not None and not header.is_leaf:
            trace.append(header)
            node = self.get_node(header.subtree_hash)
            header = node.get_child_header_for(key)
            if header is None and node.children:
                header = node.children[-1]
        if header is not None:
            trace.append(header)
        return trace

    def _edit_tree(self, path, data=None, allow_overwrite=False, must_overwrite=False,remove=False):
        key = self.hash_path(path)
        value = None
        if data:
            value = self.cache.add(data)
        headers_to_remove = []
        headers_to_add = []
        if data:
            headers_to_add = [Header(subtree_hash=value, key_upperbound=key, is_leaf=True)]
        trace = self.get_trace(key)
        leaf = trace[-1]
        if leaf.is_leaf:
            if leaf.key_upperbound == key:
                if allow_overwrite or remove:
                    headers_to_remove.append(leaf)
                else:
                    raise ValueError('file {} already exists'.format(path))
            else:
                if must_overwrite:
                    raise ValueError('must_overwrite set but file {} not found')
                if remove:
                    raise ValueError('remove set but file {} not found')
            trace.pop()
        else:
            if must_overwrite:
                raise ValueError('must_overwrite set but file {} not found')
            if remove:
                raise ValueError('remove set but file {} not found')

        while trace:
            node = self.get_node(trace.pop().subtree_hash)
            headers = list(node.children)
            while headers_to_remove:
                headers.remove(headers_to_remove.pop())
            if headers_to_add:
                headers.extend(headers_to_add)
                headers.sort()
                headers_to_add.clear()
            headers_to_remove = [node.header()]
            if len(headers) < self.b // 2 and trace:
                parent = self.get_node(trace[-1].subtree_hash)
                if len(parent.children) > 1:
                    i = bisect.bisect_left(parent.children, node.header())
                    assert parent.children[i] == node.header()
                    if i == 0:
                        sibling_header = parent.children[1]
                    else:
                        sibling_header = parent.children[i-1]
                    assert not sibling_header.is_leaf
                    sibling = self.get_node(sibling_header.subtree_hash)
                    headers.extend(sibling.children)
                    headers.sort()
                    headers_to_remove.append(sibling_header)
            if len(headers) == 1 and not headers[0].is_leaf:
                # case where tree becomes shorter
                # must be root
                assert not trace
                child = headers[0]
                node = self.get_node(child.subtree_hash)
                headers_to_add = headers
            elif len(headers) > self.b:
                headers.sort()
                left_node = self.create_node(headers[:self.b//2])
                right_node = self.create_node(headers[self.b//2:])
                headers_to_add = [left_node.header(), right_node.header()]
            else:
                node = self.create_node(headers)
                headers_to_add = [node.header()]
        if len(headers_to_add) > 1:
            node = self.create_node(headers_to_add)
        assert headers_to_remove == [self.get_node(self.root_hash).header()]
        #uncertain if this is the correct node. pls think this through more later
        #maybe we should write root hash to a file
        self.root_hash = node.nodehash
        return self.root_hash

    def add(self, path, data, allow_overwrite=False, must_overwrite=False):
        return self._edit_tree(path,data,allow_overwrite,must_overwrite,False)

    def remove(self, path):
        return self._edit_tree(path,data=None,remove=True)

    def edit(self, path, data):
        return self._edit_tree(path, data, allow_overwrite=True, must_overwrite=True, remove=False)

    #verfies that known data matches the data at that path
    def verify(self, path, data):
        return self.download(path) == data

    def ls(self, path):
        raise NotImplementedError()

    def download(self, path):
        key = self.hash_path(path)
        trace = self.get_trace(key)
        header = trace[-1]
        if not header.is_leaf or header.key_upperbound != key:
            raise KeyError()
        data = self.cache.get(header.subtree_hash)
        return data

    def prune(self):
        # maybe
        raise NotImplementedError()
