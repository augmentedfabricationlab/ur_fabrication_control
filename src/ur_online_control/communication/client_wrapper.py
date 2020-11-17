'''
Created on 11.10.2017

@author: rustr
'''
from __future__ import print_function
import time
import sys

if (sys.version_info > (3, 0)):
    python_version = 3
else:
    python_version = 2

import ur_online_control.communication.container as container
from ur_online_control.communication.msg_identifiers import *
from ur_online_control.communication.states import *

if python_version == 2:
    msg_identifier_names = {v: k for k, v in msg_identifier_dict.iteritems()}
else:
    msg_identifier_names = {v: k for k, v in msg_identifier_dict.items()}

class ClientWrapper(object):

    def __init__(self, identifier):
        self.identifier = identifier
        self.connected = False
        self.snd_queue = None
        self.rcv_queues = None

        self.waiting_time_queue = 0.1

    def wait_for_connected(self):
        print("Waiting until client %s is connected..." % self.identifier)
        connected_clients = list(container.CONNECTED_CLIENTS.keys())
        while self.identifier not in connected_clients:
            time.sleep(0.1)
            connected_clients = list(container.CONNECTED_CLIENTS.keys())
        print("Client %s is connected." % self.identifier)
        self.connected = True
        self.snd_queue = container.SND_QUEUE.get(self.identifier)
        self.rcv_queues = container.RCV_QUEUES.get(self.identifier)
        """

        for msg_id in self.rcv_queues:
            print("msg_id", msg_id)
            msg_id_name = msg_identifier_dict_inv[msg_id]
            print("msg_id_name", msg_id_name)
            exec("self.%s_queue = " % msg_id_name[4:].lower())
            print("key", key)
        """

    def wait_for_message(self, msg_id):
        if not self.connected:
            print("Client %s is NOT yet connected." % self.identifier)
            return
        if msg_id not in self.rcv_queues:
            print("Client %s does NOT send messages of type %s." % (self.identifier, msg_identifier_names[msg_id]))
            return

        print("Waiting for message %s from %s" % (msg_identifier_names[msg_id], self.identifier))
        msg = self.rcv_queues[msg_id].get(block = True)
        return msg

    def wait_for_float_list(self):
        return self.wait_for_message(MSG_FLOAT_LIST)

    def wait_for_int(self):
        # still needs to be implemented
        return self.wait_for_message(MSG_INT)

    def wait_for_ready(self):
        state, number = container.CONNECTED_CLIENTS.get(self.identifier)
        while state != READY_TO_PROGRAM:
            time.sleep(0.1)
            state, number = container.CONNECTED_CLIENTS.get(self.identifier)
        return state
    
    def wait_for_command_executed(self, number):
        state, numex = container.CONNECTED_CLIENTS.get(self.identifier)
        while numex <= number:
            time.sleep(0.1)
            state, numex = container.CONNECTED_CLIENTS.get(self.identifier)
        return numex
    
    def wait_for_digital_in(self, number):
        msg = self.wait_for_message(MSG_DIGITAL_IN)
        print(msg)
        return msg[number] # TODO:CHECK!!
    
    def wait_for_analog_in(self, number):
        msg = self.wait_for_message(MSG_ANALOG_IN)
        print(msg)
        return msg[number] # TODO:CHECK!!

    def send(self, msg_id, msg=None):
        container.CONNECTED_CLIENTS.put(self.identifier, [EXECUTING, 0])
        self.snd_queue.put((msg_id, msg))

    def send_float_list(self, float_list):
        self.send(MSG_FLOAT_LIST, float_list)

    def send_command(self, cmd_id, msg):
        self.send(MSG_COMMAND, [cmd_id, msg])
        
    def send_command_movel(self, pose_cartesian, a=0, v=0, r=0, t=0):
        self.send_command(COMMAND_ID_MOVEL, pose_cartesian + [a, v, r, t])

    def send_command_movej(self, pose_joints, a=0, v=0, r=0, t=0):
        self.send_command(COMMAND_ID_MOVEJ, pose_joints + [a, v, r, t])
    
    #def send_command_movec(self, pose_joints, a=0, v=0, r=0, t=0):
    #    self.send_command(COMMAND_ID_MOVEC, pose_joints + [a, v, r, t])
    
    #def send_command_movep(self, pose_joints, a=0, v=0, r=0, t=0):
    #    self.send_command(COMMAND_ID_MOVEP, pose_joints + [a, v, r, t])

    def send_command_digital_out(self, number, boolean):
        self.send_command(COMMAND_ID_DIGITAL_OUT, [number, int(boolean)])

    def send_command_wait(self, time_to_wait_in_seconds):
        self.send_command(COMMAND_ID_WAIT, [time_to_wait_in_seconds])
    
    def send_command_tcp(self, tcp):
        self.send_command(COMMAND_ID_TCP, tcp)
    
    def send_command_popup(self):
        self.send_command(COMMAND_ID_POPUP, None)
    
    def quit(self):
        self.send(MSG_QUIT)
    
    def send_tcp(self, tcp):
        self.send(MSG_TCP, tcp)
    
    def send_popup(self):
        self.send(MSG_POPUP)
        
        