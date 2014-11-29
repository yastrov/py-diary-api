#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loader for user and app info:
One info for line.

cat user.txt
username
password

cat appinfo.txt
appkey or ok
key or pk
"""

def filereader(fname, encoding='utf-8'):
    """Simple file reader on generator"""
    with open(fname, 'r', encoding=encoding, errors='replace') as f:
        for line in f:
            l = line.strip()
            if l.startswith('#'):
                continue
            elif l == '':
                continue
            yield l

def load_user():
    "return username, password"
    reader = filereader('user.txt')
    return list(reader)

def load_app_info():
    "return appkey, key"
    reader = filereader('appinfo.txt')
    return list(reader)

if __name__ == '__main__':
    print(load_user())
    print(load_app_info())
