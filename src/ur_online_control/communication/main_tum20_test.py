'''
Created on 22.11.2016

@author: rustr
'''
from __future__ import print_function
import time
import sys
import os

# set the paths to find library
file_dir = os.path.dirname( __file__)
parent_dir = os.path.abspath(os.path.join(file_dir, "..", ".."))
sys.path.append(file_dir)
sys.path.append(parent_dir)

import ur_online_control.communication.container as container
from ur_online_control.communication.server import Server
from ur_online_control.communication.client_wrapper import ClientWrapper
from ur_online_control.communication.formatting import format_commands
from ur_online_control.communication.msg_identifiers import *

if len(sys.argv) > 1:
    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    ur_ip = sys.argv[3]
    print(sys.argv)
else:
    #server_address = "192.168.10.12"
    server_address = "127.0.0.1"
    server_port = 30003
    #ur_ip = "192.168.10.11"
    ur_ip = "127.0.0.1"


def main():

    # start the server
    server = Server(server_address, server_port)
    server.start()
    server.client_ips.update({"UR": ur_ip})

    # create client wrappers, that wrap the underlying communication to the sockets
    ur = ClientWrapper("UR")

    # wait for the clients to be connected
    ur.wait_for_connected()

    # now enter fabrication loop
    counter = 0
    while True: # and ur and gh connected

        # send test cmds
        # ur.send_command_digital_out(2, True) # open tool
        # ur.send_command_digital_out(2, False) # close tool

        ur.send_command_airpick(True) #send vac grip on
        ur.wait_for_ready()
        
        ur.send_command_airpick(False) #send vac grip off
        ur.wait_for_ready()

        counter += 0.01
        ur.send_command_movel([0.5+counter, 0.5, 0.5, 0., 0., 0.], v=10., a=10.) # move to a location
        ur.wait_for_ready()

        
        # read out joint values from the rcv_queue
        current_pose_joints_queue = ur.rcv_queues[MSG_CURRENT_POSE_JOINT]
        current_pose_joint = current_pose_joints_queue.get_nowait()
        print("current pose joint: ", current_pose_joint)

        print("============================================================")
        
    ur.quit()
    server.close()

    print("Please press a key to terminate the program.")
    junk = sys.stdin.readline()
    print("Done.")

if __name__ == "__main__":
    main()
