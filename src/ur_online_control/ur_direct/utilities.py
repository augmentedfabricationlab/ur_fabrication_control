import socket
import os

UR_SERVER_PORT = 30002

def is_available(ur_ip):
    syscall = "ping -r 1 -n 1 %s"
    response = os.system(syscall % ur_ip)
    if response == 0:
        return True
    else:
        return False

def send_script(ur_ip, script):
    global UR_SERVER_PORT
    try:
        s = socket.create_connection((ur_ip, UR_SERVER_PORT), timeout=2)
        s.send(script)
        print "Script sent to %s on port %i" % (ur_ip, UR_SERVER_PORT)
        s.close()
    except socket.timeout:
        print "UR with ip %s not available on port %i" % (ur_ip, UR_SERVER_PORT)
        raise
