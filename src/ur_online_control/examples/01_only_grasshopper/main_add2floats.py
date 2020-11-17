from __future__ import print_function
import time
import sys
import os

# set the paths to find library
path = os.path.dirname( __file__)
idx = path.find("ur_online_control")
libpath = os.path.abspath(path[:(idx)])
sys.path.append(libpath)

import ur_online_control.communication.container as container
from ur_online_control.communication.server import Server
from ur_online_control.communication.client_wrapper import ClientWrapper
from ur_online_control.communication.formatting import format_commands

if len(sys.argv) > 1:
    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    print(sys.argv)
else:
    server_address = "127.0.0.1"
    server_port = 30003


def main():

    # start the server
    server = Server(server_address, server_port)
    server.start()
    
    # create client wrappers, that wrap the underlying communication to the sockets
    gh = ClientWrapper("GH")

    # wait for the clients to be connected
    gh.wait_for_connected()

    # now enter fabrication loop
    while True: # and ur and gh connected
        # let gh control if we should continue
        continue_fabrication = gh.wait_for_int()
        print("continue_fabrication: %i" % continue_fabrication)
        if not continue_fabrication:
            break
        
        float_list = gh.wait_for_float_list()

        # do some calculation
        x, y = float_list
        sum = x + y
        print("%f + %f = %f" % (x, y, sum))
        
        gh.send_float_list([sum])
        
    gh.quit()
    server.close()
    time.sleep(2)
    print("Done.")

if __name__ == "__main__":
    main()
