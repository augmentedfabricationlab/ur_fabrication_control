"""
Created on 15.10.2017

@author: rustr
"""

__all__ = [
    'flatten_list',
    'divide_list_by_number',
    'isclose',
    'islist'
]


def flatten_list(array):
    return [item for sublist in array for item in sublist]

 
def divide_list_by_number(array, number):
    if len(array) % number != 0:
        raise Exception("len(array) % number != 0")
    return [array[x:x+number] for x in range(0, len(array), number)]

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def islist(item):
    return isinstance(item, list)