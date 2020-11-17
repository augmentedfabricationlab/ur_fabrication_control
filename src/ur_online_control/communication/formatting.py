'''
Created on 12.10.2017

@author: rustr
'''

from ur_online_control.utilities.lists import divide_list_by_number

def divide_list(array, number):
    """Create sub-lists of the list defined by number. 
    """
    if len(array) % number != 0:
        raise Exception("len(alist) % number != 0")
    else:
        return [array[x:x+number] for x in range(0, len(array), number)]

def format_commands(msg_float_list, len_commands):
    commands = divide_list_by_number(msg_float_list, len_commands)
    return commands