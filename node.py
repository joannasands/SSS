class Node(object):
    def __init__(self,list_of_headers):
        self.children = list_of_headers
        self.nodehash = None #add in call to hash function

    @staticmethod
    def deserialize(data):
    	raise NotImplementedError()

    def serialize(self):
    	raise NotImplementedError()

    def getHeaderForKey(self,key):
    	for child in self.children:
    		if key <= child.key_upperbound:
    			return child
    	return None




class Header(object):
	def __init__(self,subtree_hash,leaf,key_upperbound):
		self.subtree_hash = subtree_hash
		self.leaf = leaf
		self.key_upperbound = key_upperbound

	def serialize(self):
		raise NotImplementedError()


#needs serialize, list of h1,....hk, list
#list of whether the children are nodes
#list of the upperbound of the keys of each child, or the hash if it is a leaf

#want to be able to serialize and deserialize