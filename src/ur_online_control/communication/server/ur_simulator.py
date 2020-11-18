'''
Created on 21.10.2017

@author: rustr
'''
from base_client import BaseClient
from ur_online_control.communication.msg_identifiers import *
import time
import struct
import random

class URClient(BaseClient):
    
    def __init__(self, host = '127.0.0.1', port = 30003): 
        super(URClient, self).__init__("UR10", host, port)
        self.ghenv = None
        self.num = 0
    
    def stdout(self, msg):
        print(msg)
    
    def send_command_received(self, counter):
        self._send(MSG_COMMAND_RECEIVED, counter)
            
    def send_command_executed(self, counter):
        self._send(MSG_COMMAND_EXECUTED, counter)
    
    def send_joint_state(self, counter):
        self.num += 0.01
        MULT=100000.
        #joints = [int(random.random()*MULT) for i in range(6)]
        joints = [int(self.num*MULT) for i in range(6)]
        self._send(MSG_CURRENT_POSE_JOINT, joints)
        
    def _format_other_messages(self, msg_id, msg = None):
        if msg_id == MSG_COMMAND_RECEIVED or msg_id == MSG_COMMAND_EXECUTED:
            msg_snd_len = 4 + 4
            params = [msg_snd_len, msg_id, msg]
            buf = struct.pack(self.byteorder + "3i", *params)
            return buf
    
    def _process_other_messages(self, msg_len, msg_id, raw_msg):
        if msg_id == MSG_COMMAND:
        
            self.stdout("Received MSG_COMMAND")
            msg = struct.unpack_from(self.byteorder + "%ii" % int((msg_len-4)/4), raw_msg)
            cmd_id = msg[0]
            counter = msg[1]
            rmsg = msg[2:]
            
            print("cmd_id: ", cmd_id)
            print("counter: ", counter)
            print("msg: ", rmsg)

            self.send_command_received(counter)
            time.sleep(1)
            self.send_command_executed(counter)
            self.send_joint_state(counter)
        else:
            self.stdout("Message identifier unknown: %d, message: %s" % (msg_id, raw_msg))

                
if __name__ == "__main__":
    #server_address = "192.168.10.12"
    server_address = "127.0.0.1"
    server_port = 30003
    client = URClient(server_address, server_port)
    client.connect_to_server()    
    client.start()
    #client.send(MSG_FLOAT_LIST, [1.2, 3.6, 4, 6, 7])
    #client.send(MSG_INT, 1)
    #client.send(MSG_FLOAT_LIST, [1.2, 3.6, 4, 6, 7])
    