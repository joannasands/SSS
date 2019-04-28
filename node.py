import hashlib
from enum import Enum

class NodeType(Enum):
        INTERNAL_NODE = 0
        FILE = 1
        DIRECTORY = 2

class Node(object):
    def __init__(self, children):
        self.children = tuple(sorted(children))
        self.nodehash = hashlib.sha256(self.serialize()).hexdigest()

    @staticmethod
    def deserialize(data):
        if len(data) % Header.SIZE_BYTES:
            raise ValueError()
        children = [Header.deserialize(data[i:i+Header.SIZE_BYTES]) for i in range(0, len(data), Header.SIZE_BYTES)]
        return Node(children)

    def serialize(self):
        return b''.join(child.serialize() for child in self.children)

    def get_child_header_for(self, key):
        for child in self.children:
            if key <= child.key_upperbound:
                return child
        return None

    def header(self):
        upperbound = self.children[-1].key_upperbound if len(self.children) > 0 else 'FFFF'*16
        return Header(self.nodehash,upperbound,NodeType.INTERNAL_NODE)

    def __repr__(self):
        return '{}(nodehash={}, children={})'.format(self.__class__.__name__, self.nodehash, self.children)


class Header(object):
    SIZE_BYTES = 65

    def __init__(self, subtree_hash, key_upperbound, node_type):
        self.subtree_hash = subtree_hash
        self.key_upperbound = key_upperbound
        self.node_type = node_type

    @staticmethod
    def deserialize(data):
        return Header(data[0:32].hex(),data[32:64].hex(),NodeType(data[64]))

    def serialize(self):
        return bytes.fromhex(self.subtree_hash) + bytes.fromhex(self.key_upperbound) + bytes([self.node_type.value])

    def __lt__(self,other):
        return (self.key_upperbound,self.subtree_hash,self.node_type.value) < (other.key_upperbound,other.subtree_hash,other.node_type.value)

    def __eq__(self,other):
        return self.serialize() == other.serialize()

    def __repr__(self):
        return '{}(subtree_hash={}, key_upperbound={}, node_type={})'.format(self.__class__.__name__, self.subtree_hash, self.key_upperbound, self.node_type)

#needs serialize, list of h1,....hk, list
#list of whether the children are nodes
#list of the upperbound of the keys of each child, or the hash if it is a leaf

#want to be able to serialize and deserialize
