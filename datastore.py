import os
import tempfile

import dropbox

class DataStore(object):
    def get(self, path):
        return self._get(path)

    def set(self, path, data):
        return self._set(path, data)

    def _get(self, path):
        raise NotImplementedError()

    def _set(self, path, data):
        raise NotImplementedError()


class DictionaryStore(DataStore):
    def __init__(self):
        self._d = dict()

    def _get(self, path):
        return self._d[path]

    def _set(self, path, data):
        self._d[path] = data


class DiskStore(DataStore):
    def __init__(self, directory):
        os.makedirs(directory, exist_ok=True)
        self.directory = directory

    def _get(self, path):
        total_path = os.path.join(self.directory, path)
        try:
            data = open(total_path, 'rb').read()
        except IOError as err:
            print('{}: {}'.format(type(err).__name__, err))
            return None
        return data

    def _set(self, path, data):
        total_path = os.path.join(self.directory, path)
        if not os.path.exists(total_path):
            fd, tmp = tempfile.mkstemp()
            try:
                with os.fdopen(fd, 'wb') as f:
                    f.write(data)
                os.replace(tmp, total_path)
                tmp = None
            finally:
                if tmp is not None:
                    try:
                        os.unlink(tmp)
                    except:
                        pass


class DropboxStore(DataStore):
    def __init__(self, token, isTest = False):
        self.dbx = dropbox.Dropbox(token)
        self.isTest = isTest

    def _get(self, path):
        if self.isTest:
            total_path = "/test/" + path
        else:
            total_path = "/merkle/" + path
        md, res = self.dbx.files_download(total_path)
        data = res.content
        return data

    def _set(self, path, data):
        if self.isTest:
            total_path = "/test/" + path
        else:
            total_path = "/merkle/" + path
        res = self.dbx.files_upload(
            data, total_path, dropbox.files.WriteMode.overwrite,
            mute=True)
        return res
