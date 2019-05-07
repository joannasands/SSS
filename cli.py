import argparse
import readline
import os

from client import Client
from datastore import DictionaryStore, DiskStore, DropboxStore


def run(args):
    if args.mode == 'db':
        with open(args.dropbox_key, 'r') as f:
            store = DropboxStore(f.readline().strip(), False)
    elif args.mode == 'disk':
        store = DiskStore(args.disk_path)
    else:
        store = DictionaryStore()

    if os.path.isfile(args.root_file):
        root_hash = open(args.root_file, 'r').readlines()[-1].strip()
        client = Client(store, root_hash=root_hash)
    else:
        client = Client(store)

    new_root = None
    file_path = args.file_path
    if args.command == 'remove':
        new_root = client.remove(args.dropbox_path)
    elif args.command == 'add':
        if file_path is not None:
            f = open(file_path, 'r')
            data = f.read().encode('utf-8')
            f.close()
            new_root = client.add(args.dropbox_path,data)
        else:
            raise ValueError('missing file_path argument, no data to add')
    elif args.command == 'edit':
        if file_path is not None:
            f = open(file_path, 'r')
            data = f.read().encode('utf-8')
            f.close()
            new_root = client.edit(args.dropbox_path,data)
        else:
            raise ValueError('missing file_path argument, no data to edit')
    elif args.command == 'download':
        if file_path is not None:
            data = client.download(args.dropbox_path)
            with open(file_path, 'wb') as f:
                f.write(data)
        else:
            raise ValueError('missing file_path argument, no location to download to')
    elif args.command == 'verify':
        if file_path is not None:
            f = open(args.file_path, 'r')
            data = f.read().encode('utf-8')
            f.close()
            verified = client.verify(args.dropbox_path,data)
            if verified:
                print('dropbox file matches data found at file path')
            else:
                print('dropbox file does not match data found at file path')
        else:
            raise ValueError('missing file_path argument, no data to verify')
    elif args.command == 'ls':
        print(client.ls(args.dropbox_path).decode())
    if new_root is not None:
        with open(args.root_file, 'a') as f:
            f.write(new_root + '\n')


def repl(args):
    parser = argparse.ArgumentParser(description='Takes in user input for client')
    parser.add_argument('command', choices=['remove', 'add', 'edit', 'download', 'verify', 'ls', 'exit'])
    parser.add_argument('dropbox_path')
    parser.add_argument('-file_path', default=None, required=False)
    parser.add_argument('-dropbox_key', default=args.dropbox_key, required=False)
    parser.add_argument('-root_file', default=args.root_file, required=False)
    parser.add_argument('-mode', choices=['db', 'disk', 'dict'], default=args.mode, required=False)
    parser.add_argument('-disk_path', default=args.disk_path, required=False)
    while True:
        try:
            stdin = input('> ')
            sub_args = parser.parse_args(stdin.split())
            if sub_args.command == 'exit':
                break
            run(sub_args)
        except EOFError:
            break
        except SystemExit:
            # ignore argparse errors
            pass
        except Exception as e:
            print('{}: {}'.format(e.__class__.__name__, e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Takes in user input for client')
    parser.add_argument('command', choices=['remove', 'add', 'edit', 'download', 'verify', 'ls', 'repl'])
    parser.add_argument('dropbox_path')
    parser.add_argument('-file_path', default=None, required=False)
    parser.add_argument('-dropbox_key', default='access_key.txt', required=False)
    parser.add_argument('-root_file', default='merkle_root.txt', required=False)
    parser.add_argument('-mode', choices=['db', 'disk', 'dict'], default='db', required=False)
    parser.add_argument('-disk_path', default='merkle_tree', required=False)
    args = parser.parse_args()

    if args.command == 'repl':
        repl(args)
    else:
        run(args)
