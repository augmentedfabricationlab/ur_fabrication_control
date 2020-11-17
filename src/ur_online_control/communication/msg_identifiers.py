'''
Created on 22.11.2016

@author: rustr
'''

MSG_IDENTIFIER = 1
MSG_COMMAND = 2 # [command_id, counter, position, orientation, optional values]
MSG_COMMAND_RECEIVED = 3
MSG_COMMAND_EXECUTED = 4
MSG_CURRENT_POSE_CARTESIAN = 5 # [position, orientation]
MSG_CURRENT_POSE_JOINT = 6 # [j1j2j3j4j5j6]
MSG_CURRENT_DIGITAL_IN = 7 # get a list of xx digital in number, values
MSG_CURRENT_ANALOG_IN = 20 # get a list of xx analog in number, values
MSG_ANALOG_IN = 8
MSG_ANALOG_OUT = 9
MSG_DIGITAL_IN = 10
MSG_DIGITAL_OUT = 11
MSG_SPEED = 12 # set a global speed var 0 - 1
MSG_INT_LIST = 13
MSG_FLOAT_LIST = 14
MSG_STRING = 15
MSG_QUIT = 16
MSG_INT = 17

MSG_TCP = 18
MSG_POPUP = 19
# attention 20 is set!

COMMAND_ID_MOVEL = 1 
COMMAND_ID_MOVEJ = 2
COMMAND_ID_MOVEC = 3
COMMAND_ID_MOVEP = 4
COMMAND_ID_DIGITAL_OUT = 5
COMMAND_ID_WAIT = 6
COMMAND_ID_TCP = 7
COMMAND_ID_POPUP = 8


msg_identifier_dict = {'MSG_IDENTIFIER': 1, 
                       'MSG_COMMAND': 2,
                       'MSG_COMMAND_RECEIVED': 3, 
                       'MSG_COMMAND_EXECUTED': 4, 
                       'MSG_CURRENT_POSE_CARTESIAN': 5, 
                       'MSG_CURRENT_POSE_JOINT': 6, 
                       'MSG_CURRENT_DIGITAL_IN': 7,
                       'MSG_CURRENT_ANALOG_IN': 20,
                       'MSG_ANALOG_IN': 8, 
                       'MSG_ANALOG_OUT': 9, 
                       'MSG_DIGITAL_IN': 10,
                       'MSG_DIGITAL_OUT': 11, 
                       'MSG_SPEED': 12,
                       'MSG_INT_LIST': 13, 
                       'MSG_FLOAT_LIST': 14, 
                       'MSG_STRING': 15, 
                       'MSG_QUIT': 16,
                       'MSG_INT': 17,
                       'MSG_TCP': 18,
                       'MSG_POPUP': 19
                       }

# different command identifiers are sent after msg_id MSG_COMMAND
command_identifier_dict = {'COMMAND_ID_MOVEL': 1, 
                           'COMMAND_ID_MOVEJ': 2,
                           'COMMAND_ID_MOVEC': 3,
                           'COMMAND_ID_MOVEP': 4,
                           'COMMAND_ID_DIGITAL_OUT': 5,
                           'COMMAND_ID_WAIT': 6,
                           'COMMAND_ID_TCP': 7,
                           'COMMAND_ID_POPUP': 8
                           }




