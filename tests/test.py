from threading import Thread
import socket
import struct
import time
import sys
import random

byteorder = "!"
msg = "UR"
msg = msg.encode('utf-8')
msg_snd_len = len(msg) + 4
params = [msg_snd_len, 1, msg]
order = byteorder + "2i" + str(len(msg)) +  "s"
print(order)
buf = struct.pack(order, *params)
print(buf)

MULT = 100000.
pose_cartesian = [1,2,3,4,5,6] 
a, v, r, t = [7,8,9,10]
cmd = pose_cartesian + [a, v, r, t]
msg_command_length = 4 * (len(cmd) + 1 + 1 + 1) # + msg_id, command_id, command_counter
cmd = [int(c * MULT) for c in cmd]
params = [msg_command_length, 2, 1, 0] + cmd
buf = struct.pack(byteorder + "%ii" % len(params), *params)
print(buf)

joints = [random.random() for i in range(6)]
print(joints)