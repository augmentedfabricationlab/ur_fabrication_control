'''
Created on 09.10.2017

@author: rustr
'''

def read_file_to_string(afile):
    with open(afile) as f:
        afile_str = f.read()
    return afile_str

def read_file_to_list(afile):
    return [line for line in open(afile, "r").readlines()]