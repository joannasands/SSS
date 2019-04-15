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

class DropboxStore(DataStore):
    def __init__(self, token, isTest = False):
        self.dbx = dropbox.Dropbox(token)
        self.isTest = isTest

    def _get(self, path):
        if self.isTest:
            total_path = "/test/" + path
        else:
            total_path = "/merkle/" + path
        try:
            md, res = self.dbx.files_download(total_path)
        except dropbox.exceptions.HttpError as err:
            print('*** HTTP error', err)
            return None
        data = res.content
        print(len(data), 'bytes; md:', md)
        return data

    def _set(self, path, data):
        if self.isTest:
            total_path = "/test/" + path
        else:
            total_path = "/merkle/" + path
        try:
            res = self.dbx.files_upload(
                data, total_path, dropbox.files.WriteMode.overwrite,
                mute=True)
        except dropbox.exceptions.ApiError as err:
            print('*** API error', err)
            return None
        return res
