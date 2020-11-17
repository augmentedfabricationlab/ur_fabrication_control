from threading import Thread
import socket
import struct
import time
import sys

byteorder = "!"
msg = "UR"
msg = msg.encode('utf-8')
msg_snd_len = len(msg) + 4
params = [msg_snd_len, 1, msg]
order = byteorder + "2i" + str(len(msg)) +  "s"
print(order)
buf = struct.pack(order, *params)
print(buf)