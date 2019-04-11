import argparse
import contextlib
import datetime
import os
import six
import sys
import time
import unicodedata
import dropbox

parser = argparse.ArgumentParser(description='Sync ~/Downloads to Dropbox')
parser.add_argument('token', nargs='?', default='Downloads',
                    help='your access token')

def main():
    args = parser.parse_args()
    dbx = dropbox.Dropbox(args.token);
    #upload(dbx)
    data = download(dbx)
    with open("README2.md", 'wb') as f:
        f.write(data)
        f.close()

def download(dbx):
    try:
        md, res = dbx.files_download("/hi.md")
    except dropbox.exceptions.HttpError as err:
        print('*** HTTP error', err)
        return None
    data = res.content
    print(len(data), 'bytes; md:', md)
    return data

def upload(dbx):
    with open("README.md", 'rb') as f:
        data = f.read()
    try:
        res = dbx.files_upload(
            data, "/hi.md", dropbox.files.WriteMode.overwrite,
            mute=True)
    except dropbox.exceptions.ApiError as err:
        print('*** API error', err)
        return None
    print('uploaded as', res.name.encode('utf8'))
    return res

if __name__ == '__main__':
    print(main())
