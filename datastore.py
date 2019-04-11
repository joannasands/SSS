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
    def __init__(self, token):
        self.dbx = dbx = dropbox.Dropbox(token)

    def _get(self, path):
        try:
            md, res = dbx.files_download(path)
        except dropbox.exceptions.HttpError as err:
            print('*** HTTP error', err)
            return None
        data = res.content
        print(len(data), 'bytes; md:', md)
        return data

    def _set(self, path, data):
        try:
            res = dbx.files_upload(
                data, path, dropbox.files.WriteMode.overwrite,
                mute=True)
        except dropbox.exceptions.ApiError as err:
            print('*** API error', err)
            return None
        return res
