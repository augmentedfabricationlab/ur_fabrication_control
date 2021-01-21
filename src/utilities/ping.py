'''
Created on 12.10.2017

@author: rustr
'''

import os

def is_available(ip):
    
    syscall = "ping -r 1 -n 1 %s"
    response = os.system(syscall % ip)
    if response == 0:
        return True
    else:
        return False