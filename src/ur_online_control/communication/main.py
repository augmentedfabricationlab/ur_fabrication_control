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
    gh = ClientWrapper("GH")
    ur = ClientWrapper("UR")

    # wait for the clients to be connected
    gh.wait_for_connected()
    ur.wait_for_connected()

    # now enter fabrication loop
    while True: # and ur and gh connected
        # let gh control if we should continue
        continue_fabrication = gh.wait_for_int()
        print("continue_fabrication: %i" % continue_fabrication)
        if not continue_fabrication:
            break
        # receive further information from gh
        # e.g. send number of commands:
        # number = gh.wait_for_int()
        # commands = []
        # for i in range(number):
        #       cmd = gh.wait_for_float_list()
        #       commands.append(cmd)


        picking_pose_cmd = gh.wait_for_float_list()
        savety_pose_cmd = gh.wait_for_float_list()

        len_command = gh.wait_for_int()
        commands_flattened = gh.wait_for_float_list()
        # the commands are formatted according to the sent length
        commands = format_commands(commands_flattened, len_command)
        print("We received %i commands." % len(commands))

        # 1. move to savety pose
        x, y, z, ax, ay, az, acc, vel = savety_pose_cmd
        ur.send_command_movel([x, y, z, ax, ay, az], a=acc, v=vel)
        # 2. open gripper
        ur.send_command_digital_out(2, True) # open tool
        # 3. move to picking pose
        x, y, z, ax, ay, az, acc, vel = picking_pose_cmd
        ur.send_command_movel([x, y, z, ax, ay, az], a=acc, v=vel)
        # 4. Close gripper
        ur.send_command_digital_out(2, False) # close tool
        # 5. move to savety pose
        x, y, z, ax, ay, az, acc, vel = savety_pose_cmd
        ur.send_command_movel([x, y, z, ax, ay, az], a=acc, v=vel)

        # placing path
        for i in range(0, len(commands), 3):

            savety_cmd1 = commands[i]
            placing_cmd = commands[i+1]
            savety_cmd2 = commands[i+2]

            # 5. move to savety pose 1
            x, y, z, ax, ay, az, speed, radius = savety_cmd1
            ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)
            # 6. move to placing pose
            x, y, z, ax, ay, az, speed, radius = placing_cmd
            ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)
            # 7. wait
            ur.send_command_wait(2.)
            # 8. open gripper
            ur.send_command_digital_out(2, True) # open tool
            # 7. wait
            ur.send_command_wait(1.)
            # 9. move to savety pose 2
            x, y, z, ax, ay, az, speed, radius = savety_cmd2
            ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)

            # 1. move to savety pose
            x, y, z, ax, ay, az, acc, vel = savety_pose_cmd
            ur.send_command_movel([x, y, z, ax, ay, az], a=acc, v=vel)
            # 2. open gripper
            ur.send_command_digital_out(2, True) # open tool
            # 3. move to picking pose
            x, y, z, ax, ay, az, acc, vel = picking_pose_cmd
            ur.send_command_movel([x, y, z, ax, ay, az], a=acc, v=vel)
            # 4. Close gripper
            ur.send_command_digital_out(2, False) # close tool
            # 5. move to savety pose
            x, y, z, ax, ay, az, acc, vel = savety_pose_cmd
            ur.send_command_movel([x, y, z, ax, ay, az], a=acc, v=vel)


        ur.wait_for_ready()
        gh.send_float_list(commands[0])
        print("============================================================")
        break
        """
        ur.wait_for_ready()
        # wait for sensor value
        digital_in = ur.wait_for_digital_in(number)
        current_pose_joint = ur.wait_for_current_pose_joint()
        current_pose_cartesian = ur.get_current_pose_cartesian()
        # send further to gh
        gh.send_float_list(digital_in)
        gh.send_float_list(current_pose_joint)
        gh.send_float_list(current_pose_cartesian)
        """
    ur.quit()
    gh.quit()
    server.close()

    print("Please press a key to terminate the program.")
    junk = sys.stdin.readline()
    print("Done.")

if __name__ == "__main__":
    main()
