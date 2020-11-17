'''
Created on 23.08.2016

@author: rustr
'''

import select
import socket
from threading import Thread
import time
import struct
import sys

from .base_client_socket import *
from .actuator_socket import *

if (sys.version_info > (3, 0)):
    python_version = 3
else:
    python_version = 2



class Server(object):

    def __init__(self, address = '127.0.0.1', port = 30003):

        self.address = address
        self.port = port
        self.client_sockets = []
        self.client_ips = {}
        self.input = []
        self.running = False
        self.notification_messages = []
        self.start_listening()

    def start_listening(self):
        backlog = 5
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.address, self.port))
        self.server.listen(backlog)
        self.input = [self.server]
        self.stdout("Running on address %s and port %d." % (self.address, self.port))
        self.running = True

    def update(self):
        pass

    def stdout(self, msg):
        print("SERVER: %s" % msg)

    def start(self):
        self.running_thread = Thread(target = self.run)
        self.running_thread.daemon = False
        self.running_thread.start()

    def create_client_socket(self, sock, ip):
        # This method can be overwritten to specify the client socket
        if ip in self.client_ips.values():
            if python_version == 2:
                inv_map = {v: k for k, v in self.client_ips.iteritems()}
            else:
                inv_map = {v: k for k, v in self.client_ips.items()}
            print("%sSocket(sock, ip, self)" % inv_map[ip])
            client_socket = eval("%sSocket(sock, ip, self)" % inv_map[ip])
        else:
            client_socket = BaseClientSocket(sock, ip, self)
        return client_socket

    def run(self):
        timeout = 0.008

        while self.running:
            try:
                inputready, outputready, exceptready = select.select(self.input, [], [], timeout)

            except socket.error as e:

                if e.errno == socket.errno.EBADF: # raise error(EBADF, 'Bad file descriptor')
                    self.stdout(len(self.input))
                    #pass
                else:
                    raise

            except select.error:
                self.stdout("An operation was attempted on something that is not a socket")

            for s in inputready:
                if s == self.server:
                    try:
                        sock, address = self.server.accept()
                        self.incoming_connection(sock, address)
                    except socket.error as e:
                        break
                elif s == sys.stdin: # close on key input
                    # handle standard input
                    junk = sys.stdin.readline()
                    self.running = False
                    break


        self.server.close()

    def incoming_connection(self, sock, address):
        """ Accept any connection and create a ClientSocket. """
        ip, port = address
        self.stdout("________________incoming connection from %s, at port %d. " % (ip, port))

        self.input.append(sock)
        client_socket = self.create_client_socket(sock, ip)
        client_socket.start()
        self.client_sockets.append(client_socket)
        self.update()

    def remove_client(self, client_socket):
        try:
            self.input.remove(client_socket.socket)
            self.client_sockets.remove(client_socket)
            self.stdout("Removed client %s" % client_socket.identifier)
        except ValueError:
            pass

    def close(self):
        self.running = False
        self.server.close()
        try:
            self.running_thread.join()
            self.stdout("Close done.")
        except:
            self.stdout("Cannot close thread.")
            pass

    def notify(self, msg):
        self.stdout("Received notification.")
        self.notification_messages.append(msg)

if __name__ == "__main__":

    server = Server(address = '192.168.10.12', port = 30003)
    server.run()
