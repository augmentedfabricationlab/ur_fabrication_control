'''
Created on 15.10.2017

@author: rustr
'''

def flatten_list(array):
    return [item for sublist in array for item in sublist]

 
def divide_list_by_number(array, number):
    if len(array) % number != 0:
        raise Exception("len(array) % number != 0")
    return [array[x:x+number] for x in range(0, len(array), number)]
