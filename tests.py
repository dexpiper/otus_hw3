#!/usr/bin/env python3
'''
Running tests.

Usage:
$ python3 tests.py [testfile, optional (default: all tests)] [-v, --verbose]
'''
import argparse
import subprocess
import os
import fnmatch


def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


#
# Running tests
#
argpars = argparse.ArgumentParser()
argpars.add_argument('-v', '--verbose', help='More verbose test information',
                     action='store_true')
argpars.add_argument('testfile', nargs='?', default='all',
                     help='Specify testfile to use')
args = argpars.parse_args()

command = ['python', '-m', 'unittest']

if args.testfile == 'all':
    command += ['discover', '.', "test_*.py"]
else:
    path = find(f'test_{args.testfile}.py', 'tests')[0]
    assert os.path.isfile(path), f'Test file "{args.testfile}" not found'
    print(path)
    command.append(path)
if args.verbose:
    print('Running in verbose mode')
    command.append('-v')

subprocess.run(command)
