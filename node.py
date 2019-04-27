import hashlib

class Node(object):
    def __init__(self, children):
        self.children = children
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
        return Header(self.nodehash,upperbound,False)

    def __repr__(self):
        return '{}(nodehash={}, children={})'.format(self.__class__.__name__, self.nodehash, self.children)


class Header(object):
    SIZE_BYTES = 65

    def __init__(self, subtree_hash, key_upperbound, is_leaf):
        self.subtree_hash = subtree_hash
        self.key_upperbound = key_upperbound
        self.is_leaf = is_leaf

    @staticmethod
    def deserialize(data):
        return Header(data[0:32].hex(),data[32:64].hex(),bool(data[64]))

    def serialize(self):
        return bytes.fromhex(self.subtree_hash) + bytes.fromhex(self.key_upperbound) + bytes([self.is_leaf])

    def __lt__(self,other):
        return (self.key_upperbound,self.subtree_hash,self.is_leaf) < (other.key_upperbound,other.subtree_hash,other.is_leaf)

    def __eq__(self,other):
        return self.serialize() == other.serialize()

    def __repr__(self):
        return '{}(subtree_hash={}, key_upperbound={}, is_leaf={})'.format(self.__class__.__name__, self.subtree_hash, self.key_upperbound, self.is_leaf)

#needs serialize, list of h1,....hk, list
#list of whether the children are nodes
#list of the upperbound of the keys of each child, or the hash if it is a leaf

#want to be able to serialize and deserialize