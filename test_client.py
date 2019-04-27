import pytest

# import SSS
from client import Client
from datastore import DictionaryStore, DropboxStore
from node import Node, Header

def test_add_and_download():
    store = DictionaryStore()
    client = Client(store)
    files = [
        ('/chris/terman.says', b'andrewhe reigns supreme'),
        ('/andrew/he.says', b'I am so f*** fast'),
        ('/andrew/he/also.says', b'Rust is so beautiful')
    ]

    for path, message in files:
        print(message)
        client.add(path, message)

    for path, message in files:
        m = client.download(path)
        assert m == message

    client.cache.d.clear()
    for path, message in files:
        m = client.download(path)
        assert m == message

def test_add_and_download_dropbox():
    f = open("access_key.txt", 'r')
    store = DropboxStore(f.readline().strip(), True)
    f.close()
    client = Client(store)
    files = [
        ('/chris/terman.says', b'andrewhe reigns supreme'),
        ('/andrew/he.says', b'I am so f*** fast'),
        ('/andrew/he/also.says', b'Rust is so beautiful')
    ]

    for path, message in files:
        print(message)
        client.add(path, message)

    client.cache.d.clear()
    for path, message in files:
        m = client.download(path)
        assert m == message

def test_remove():
    store = DictionaryStore()
    client = Client(store)
    files = [
        ('/chris/terman.says', b'andrewhe reigns supreme'),
        ('/andrew/he.says', b'I am so f*** fast'),
        ('/andrew/he/also.says', b'Rust is so beautiful')
    ]

    for path, message in files:
        print(message)
        client.add(path, message)

    client.remove(path=files[0][0])

    for i, (path, message) in enumerate(files):
        if i==0:
            try:
                m = client.download(path)
                raise ValueError()
            except KeyError:
                pass
        else:
            m = client.download(path)
            assert m == message


def test_serialize_and_deserialize():
    head = Header('2Ef0'*16,'FFFF'*16,True)
    serial = head.serialize()
    de = Header.deserialize(serial)
    assert de.subtree_hash == '2ef0'*16
    assert de.key_upperbound =='ffff'*16
    assert de.is_leaf == True
