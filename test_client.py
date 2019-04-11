import pytest

import SSS.client
import SSS.datastore

def test_add_and_download():
    store = SSS.datastore.DictionaryStore()
    client = SSS.client.Client(store)
    files = [
        ('/chris/terman.says', 'andrewhe reigns supreme'),
        ('/andrew/he.says', 'I am so f*** fast'),
        ('/andrew/he/also.says', 'Rust is so beautiful'),
    ]

    for path, message in files:
        client.add(path, message)

    for path, message in files:
        m = client.download(path)
        assert m == message
