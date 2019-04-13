import pytest

# import SSS
import SSS.client
import SSS.datastore
import SSS.node

def test_add_and_download():
    store = SSS.datastore.DictionaryStore()
    client = SSS.client.Client(store)
    files = [
        ('/chris/terman.says', b'andrewhe reigns supreme'),
        ('/andrew/he.says', b'I am so f*** fast'),
        ('/andrew/he/also.says', b'Rust is so beautiful'),
    ]

    for path, message in files:
        print(message)
        client.add(path, message)

    for path, message in files:
        m = client.download(path)
        assert m == message

def test_serialize_and_deserialize():
    head = SSS.node.Header('2Ef0'*16,'FFFF'*16,True)
    serial = head.serialize()
    de = SSS.node.Header.deserialize(serial)
    assert de.subtree_hash == '2ef0'*16
    assert de.key_upperbound =='ffff'*16
    assert de.is_leaf == True
