'''
Created on 10.10.2017

@author: rustr
'''

READY_TO_PROGRAM = 1 # the buffer of the robot is empty, he is ready to receive commands (number = stacksize)
EXECUTING = 2 # the robot is executing the command
READY_TO_RECEIVE = 3 # the buffer of the robot has space, he is ready to receive the next command
COMMAND_EXECUTED = 6