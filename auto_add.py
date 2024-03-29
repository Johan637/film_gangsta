#!/usr/bin/python3

import os


if __name__ == '__main__':
    filename = 'git.list'
    with open(filename, 'rt') as list:
        for line in list:
            file = line.strip()
            if file:
                os.system(f'git add {file}')
                print(f'file \'{file}\' added')
