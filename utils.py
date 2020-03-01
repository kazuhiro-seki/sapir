#! -*- coding: utf-8 -*-

"""
utils
"""

import gzip

'''
File opener depending on suffix
'''
def open_by_suffix(filename):
    if filename == None or filename == "":
        print("Error: Specify input file name")
        exit()
    if filename.endswith('.gz'):
        return gzip.open(filename, 'rt')
    elif filename.endswith('.bz2'):
        return bz2.BZ2file(filename, 'r')
    else: # assume text file
        return open(filename, 'r')

