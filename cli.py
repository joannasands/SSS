import argparse
from client import Client
from datastore import DictionaryStore,DropboxStore

parser = argparse.ArgumentParser(description='Takes in user input for client')

parser.add_argument('command',choices=['remove','add','edit','download','verify'])
parser.add_argument('dropbox_path')
parser.add_argument('-file_path',default=None,required=False)
parser.add_argument('-dropbox_key', default=None,required=False)
parser.add_argument('-root', default=None,required=False)
args = parser.parse_args()

if args.dropbox_key is not None:
	store = DropboxStore(args.dropbox_key, False)
else:
    store = DictionaryStore()
if args.root is not None:
	client = Client(store,root_hash=args.root)
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
		raise ValueError("missing file_path argument, no data to add")
elif args.command == 'edit':
	if file_path is not None:
		f = open(file_path, 'r')
		data = f.read().encode('utf-8')
		f.close()
		new_root = client.edit(args.dropbox_path,data)
	else:
		raise ValueError("missing file_path argument, no data to edit")
elif args.command == 'download':
	if file_path is not None:
		data = client.download(args.dropbox_path)
		f = open(file_path, 'w')
		f.write(data)
		f.close()
	else:
		raise ValueError("missing file_path argument, no location to download to")
elif args.command == 'verify':
	if file_path is not None:
		f = open(args.file_path, 'r')
		data = f.read().encode('utf-8')
		f.close()
		verified = client.verify(args.dropbox_path,data)
		if verified:
			print("dropbox file matches data found at file path")
		else:
			print("dropbox file does not match data found at file path")
	else:
		raise ValueError("missing file_path argument, no data to verify")
print("new root: ", new_root)
