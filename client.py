import bisect
import hashlib
import os
import copy

from datastore import DictionaryStore
from node import Node, Header, NodeType


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
        if root_header.node_type != NodeType.INTERNAL_NODE:
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
        while header is not None and header.node_type == NodeType.INTERNAL_NODE:
            trace.append(header)
            node = self.get_node(header.subtree_hash)
            header = node.get_child_header_for(key)
            if header is None and node.children:
                header = node.children[-1]
        if header is not None:
            trace.append(header)
        return trace

    def _edit_tree(self, path, data=None, allow_overwrite=False, must_overwrite=False,remove=False, node_type=NodeType.FILE):
        key = self.hash_path(path)
        value = None
        if data:
            value = self.cache.add(data)
        headers_to_remove = []
        headers_to_add = []
        if data:
            headers_to_add = [Header(subtree_hash=value, key_upperbound=key, node_type=node_type)]
        trace = self.get_trace(key)
        leaf = trace[-1]
        if leaf.node_type != NodeType.INTERNAL_NODE:
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
                    assert sibling_header.node_type == NodeType.INTERNAL_NODE
                    sibling = self.get_node(sibling_header.subtree_hash)
                    headers.extend(sibling.children)
                    headers.sort()
                    headers_to_remove.append(sibling_header)
            if len(headers) == 1 and headers[0].node_type == NodeType.INTERNAL_NODE:
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

    def _add(self, path, data, allow_overwrite=False, must_overwrite=False, node_type=NodeType.FILE):
        return self._edit_tree(path,data,allow_overwrite,must_overwrite,False,node_type)

    def _add_to_dir(self, path, check_root=True):
        directory = os.path.dirname(path)
        if directory == os.path.dirname(directory):
            if check_root:
                check_root = False
            else:
                return
        base = os.path.basename(path).encode('utf-8')
        try:
            current_ls, node_type = self.get(directory)
            if node_type==NodeType.FILE:
                raise ValueError('Tried to add subdirectory to a file')
            files = set(current_ls.split(b'\n'))
            if base in files:
                raise ValueError('File already exists')
            files.add(base)
            new_ls = b'\n'.join(sorted(files))
            return self.edit(directory, new_ls, node_type=NodeType.DIRECTORY)
        except KeyError:
            self._add_to_dir(directory, check_root=check_root)
            new_ls = base
            return self._add(directory, new_ls, node_type=NodeType.DIRECTORY)

    def add(self, path, data, allow_overwrite=False, must_overwrite=False):
        abs_path = os.path.normpath(os.path.join('/', path))
        self._add_to_dir(abs_path)
        return self._add(path, data, allow_overwrite=False, must_overwrite=False, node_type=NodeType.FILE)

    def _rm_from_dir(self, path, check_root=True):
        directory = os.path.dirname(path)
        if directory == os.path.dirname(directory):
            if check_root:
                check_root = False
            else:
                return
        base = os.path.basename(path).encode('utf-8')
        current_ls, node_type = self.get(directory)
        if node_type==NodeType.FILE:
            raise ValueError('Tried to add subdirectory to a file')
        files = set(current_ls.split(b'\n'))
        if base not in files:
            raise ValueError('File doesn\'t exist')
        files.remove(base)
        if not files:
            self._rm_from_dir(directory, check_root=check_root)
            return self._remove(directory, node_type=NodeType.DIRECTORY)
        else:
            new_ls = b'\n'.join(sorted(files))
            return self.edit(directory, new_ls, node_type=NodeType.DIRECTORY)

    def _remove(self, path, node_type):
        return self._edit_tree(path,data=None,remove=True, node_type=node_type)

    def remove(self, path):
        abs_path = os.path.normpath(os.path.join('/', path))
        self._rm_from_dir(abs_path)
        return self._remove(path, NodeType.FILE)

    def edit(self, path, data, node_type=NodeType.FILE):
        return self._edit_tree(path, data, allow_overwrite=True, must_overwrite=True, remove=False, node_type=node_type)

    #verfies that known data matches the data at that path
    def verify(self, path, data):
        return self.download(path) == data

    def ls(self, path):
        data, node_type = self.get(path)
        if node_type == NodeType.DIRECTORY:
            return data
        raise KeyError()

    def get(self, path):
        key = self.hash_path(path)
        trace = self.get_trace(key)
        header = trace[-1]
        if header.node_type==NodeType.INTERNAL_NODE or header.key_upperbound != key:
            raise KeyError()
        data = self.cache.get(header.subtree_hash)
        return (data, header.node_type)

    def download(self, path):
        data, node_type = self.get(path)
        if node_type == NodeType.FILE:
            return data
        raise KeyError()

    def prune(self):
        # maybe
        raise NotImplementedError()
