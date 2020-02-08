from sys import argv
from os import listdir, path
from shutil import rmtree
from re import match

if len(argv) != 2:
    print('usage: python3 clear_pycache.py DIR')
    exit()

def list_dir(dir, pattern):
    dir = path.abspath(dir)
    for p in listdir(dir):
        d = path.join(dir, p)
        if path.isdir(d):
            if match(pattern, p):
                yield d
            else:
                for d in list_dir(d, pattern):
                    yield d

for dir in list_dir(argv[1], '__pycache__'):
    ans = input(f'remove {dir}? ').upper()
    if ans == 'Y' or ans == 'YES':
        rmtree(dir)



        