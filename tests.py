#!/usr/bin/env python3
'''
Running tests.

Usage:
$ python3 tests.py [testfile, optional (default: all tests)] [-v, --verbose]
'''
import argparse
import subprocess
import os

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
    path = f'tests/test_{args.testfile}.py'
    assert os.path.isfile(path), f'Test file "{args.testfile}" not found'
    command.append(path)
if args.verbose:
    print('Running in verbose mode')
    command.append('-v')

subprocess.run(command)
