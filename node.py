class Node(object):
    def __init__(self, children):
        self.children = children
        self.nodehash = None #add in call to hash function

    @staticmethod
    def deserialize(data):
        if len(data) % Header.SIZE_BYTES:
            raise ValueError()
        children = [Header.serialize(data[i:i+Header.SIZE_BYTES]) for i in range(0, len(data), Header.SIZE_BYTES)]
        return Node(children)

    def serialize(self):
        return b''.join(child.serialize() for child in self.children)

    def get_child_header_for(self, key):
    	for child in self.children:
    		if key <= child.key_upperbound:
    			return child
    	return None




class Header(object):
    SIZE_BYTES = 65

	def __init__(self, subtree_hash, is_leaf, key_upperbound):
		self.subtree_hash = subtree_hash
		self.is_leaf = is_leaf
		self.key_upperbound = key_upperbound

    @staticmethod
    def deserialize(data):
    	raise NotImplementedError()

	def serialize(self):
		raise NotImplementedError()


#needs serialize, list of h1,....hk, list
#list of whether the children are nodes
#list of the upperbound of the keys of each child, or the hash if it is a leaf

#want to be able to serialize and deserialize