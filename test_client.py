import pytest
import tempfile

# import SSS
from client import Client
from datastore import DictionaryStore, DiskStore, DropboxStore
from node import Node, Header, NodeType

def run_add_and_download(store):
    client = Client(store)
    files = [
        ('/chris/terman.says', b'andrewhe reigns supreme'),
        ('/andrew/he.says', b'I am so f*** fast'),
        ('/andrew/he/also.says', b'Rust is so beautiful')
    ]

    for path, message in files:
        # print(message)
        client.add(path, message)

    for path, message in files:
        m = client.download(path)
        assert m == message

    client.cache.d.clear()
    for path, message in files:
        m = client.download(path)
        assert m == message

def test_add_and_download_dict():
    store = DictionaryStore()
    run_add_and_download(store)

def test_add_and_download_disk():
    with tempfile.TemporaryDirectory() as directory:
        store = DiskStore(directory)
        run_add_and_download(store)

def test_add_and_download_dropbox():
    with open("access_key.txt", 'r') as f:
        store = DropboxStore(f.readline().strip(), True)
    run_add_and_download(store)

def test_remove():
    store = DictionaryStore()
    client = Client(store)
    files = [
        ('/chris/terman.says', b'andrewhe reigns supreme'),
        ('/andrew/he.says', b'I am so f*** fast'),
        ('/andrew/he/also.says', b'Rust is so beautiful')
    ]

    for path, message in files:
        # print(message)
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

def test_large():
    store = DictionaryStore()
    client = Client(store, b=6)
    num_files = 100
    files = [('/%d.txt' % i, b'This is file %d' % i) for i in range(num_files)]

    for path, message in files:
        client.add(path, message)

    for path, message in files:
        m = client.download(path)
        assert m == message

    for path, message in files[:len(files)//2]:
        client.remove(path=path)

    for i, (path, message) in enumerate(files):
        if i < len(files)//2:
            try:
                m = client.download(path)
                raise ValueError()
            except KeyError:
                pass
        else:
            m = client.download(path)
            assert m == message

def test_serialize_and_deserialize():
    head = Header('2Ef0'*16,'FFFF'*16,NodeType.FILE)
    serial = head.serialize()
    de = Header.deserialize(serial)
    assert de.subtree_hash == '2ef0'*16
    assert de.key_upperbound =='ffff'*16
    assert de.node_type == NodeType.FILE
