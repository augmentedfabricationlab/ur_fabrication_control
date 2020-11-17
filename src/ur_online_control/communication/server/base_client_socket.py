'''
Created on 02.12.2013

@author: rustr
'''
from threading import Thread
import struct
from multiprocessing import Queue
import socket
import time
import sys

from ur_online_control.communication.msg_identifiers import *
from ur_online_control.communication.states import *
import ur_online_control.communication.container as container


class BaseClientSocket(object):

    """ The Client Socket is the base for the specific client sockets
    It can be used for both Receiver and Sender Sockets. """

    def __init__(self, socket, ip, parent):

        self.socket = socket
        self.ip = ip
        self.parent = parent

        #self.msg_rcv = b""
        self.msg_rcv = ""
        self.byteorder = "!" # "!" network, ">" big-endian, "<" for little-endian, see http://docs.python.org/2/library/struct.html
        #self.byteorder = "<"

        self.running = True

        self.socket.settimeout(0.008)

        self.snd_queue = Queue()

        # rcv_queues
        self.float_list_queue = Queue()
        self.string_queue = Queue()
        self.int_queue = Queue()

        self.identifier = ""

        self.byteorder_isset = False

        self.state = READY_TO_PROGRAM

    def stdout(self, msg):
        print("%s: %s" % (self.identifier, msg))


    def read(self):
        ''' The transmission protocol for messages is
        [length msg in bytes] [msg identifier] [other bytes which will be read out according to msg identifier] '''

        # 1. read msg length
        self.msg_rcv += self.socket.recv(4)

        if len(self.msg_rcv) < 4:
            return
        msg_length = struct.unpack_from(self.byteorder + "i", self.msg_rcv, 0)[0]

        # TODO: how to check this better?
        if not self.byteorder_isset:
            msg_length2 = socket.ntohl(msg_length) # convert 32-bit positive integers from network to host byte order
            if msg_length2 < msg_length:
                self.byteorder = "<"
                msg_length = msg_length2
            self.byteorder_isset = True

        # 2. read msg according to msg_length
        self.msg_rcv += self.socket.recv(msg_length)
        if len(self.msg_rcv) < (msg_length + 4):
            return

        # 3. message identifier
        msg_id = struct.unpack_from(self.byteorder + "i", self.msg_rcv[4:8], 0)[0]

        #self.stdout("Received %i ==>" % msg_id)

        # 4. rest of message, according to msg_length
        raw_msg = self.msg_rcv[8:(8 + msg_length - 4)]

        # 5. set self.msg_rcv to the rest
        self.msg_rcv = self.msg_rcv[(8 + msg_length - 4):]

        # 4. pass message id and raw message to process method
        self.process(msg_length, msg_id, raw_msg)

    def get_msg_float_list(self, msg_len, raw_msg):

        #msg_float_tuple = struct.unpack_from(self.byteorder + str((msg_len-4)/4) + "f", raw_msg.decode(encoding='UTF-8'))
        msg_float_tuple = struct.unpack_from(self.byteorder + str((msg_len-4)/4) + "f", raw_msg)
        msg_float_list = [item for item in msg_float_tuple]
        return msg_float_list

    def _process_msg_float_list(self, msg_float_list):
        self.float_list_queue.put(msg_float_list)

    def _process_msg_string(self, msg):
        self.string_queue.put(msg)

    def _process_msg_int(self, msg):
        print(msg)
        self.int_queue.put(msg)

    def _process_other_messages(self, msg_len, msg_id, raw_msg):
        self.stdout("msg_id %d" % msg_id)
        self.stdout("Message identifier unknown:  %d, message: %s" % (msg_id, raw_msg))
    
    def _format_other_messages(self, msg_id, msg):
        pass

    def process(self, msg_len, msg_id, raw_msg):

        if msg_id == MSG_IDENTIFIER:
            #message_ids = str(raw_msg).split(" ")
            #identifier = raw_msg.decode(encoding='UTF-8')
            self.identifier = str(raw_msg)
            self.stdout("Received identifier.")
            self.publish_queues()
            self.publish_client()

        elif msg_id == MSG_FLOAT_LIST:
            msg_float_list = self.get_msg_float_list(msg_len, raw_msg)
            self._process_msg_float_list(msg_float_list)

        elif msg_id == MSG_STRING:
            msg = str(raw_msg)
            self._process_msg_string(msg)

        elif msg_id == MSG_INT:
            msg = struct.unpack_from(self.byteorder + "i", raw_msg)[0]
            self._process_msg_int(msg)

        elif msg_id == MSG_QUIT:
            self.close()
        else:
            self._process_other_messages(msg_len, msg_id, raw_msg)


    def publish_queues(self):
        container.SND_QUEUE.put(self.identifier, self.snd_queue)
        container.RCV_QUEUES.put(self.identifier, {MSG_FLOAT_LIST: self.float_list_queue})
        container.RCV_QUEUES.put(self.identifier, {MSG_STRING: self.string_queue})
        container.RCV_QUEUES.put(self.identifier, {MSG_INT: self.int_queue})

    def publish_client(self):
        container.CONNECTED_CLIENTS.put(self.identifier, [self.state, 0])

    def close(self):
        self.running = False
    
    def send_command(self, command_id, msg):
        pass

    def send(self, msg_id, msg = None):
        ''' The transmission protocol for send messages is
        [length msg in bytes] [msg identifier] [other bytes which will be read out according to msg identifier]
        '''
        buf = None

        if msg_id == MSG_QUIT:
            msg_snd_len = 4
            params = [msg_snd_len, msg_id]
            buf = struct.pack(self.byteorder + "2i", *params)

        elif msg_id == MSG_FLOAT_LIST:
            msg_snd_len = struct.calcsize(str(len(msg)) + "f") + 4
            msg = [float(item) for item in msg] # change tuple to list
            params = [msg_snd_len, msg_id] + msg
            buf = struct.pack(self.byteorder + "2i" + str(len(msg)) +  "f", *params)
        
        elif msg_id == MSG_COMMAND:
            self.send_command(msg_id, msg)
            return

        else:
            buf = self._format_other_messages(msg_id, msg)
            if not buf:
                self.stdout("Message identifier unknown:  %d, message: %s" % (msg_id, msg))
                return

        try:
            self.socket.send(buf)
            self.stdout("Sent message %i." % msg_id)

        except socket.timeout:
            self.stdout("Timeout in sending, trying again...")
            time.sleep(0.5)
            self.socket.send(buf)
            self.stdout("Sent message %i." % msg_id)

        except socket.error as e:
            if e.errno == 10054 or e.errno == 10053:
                self.running = False

    def start(self):
        self.running_thread = Thread(target = self.run)
        self.running_thread.daemon = True # die if main dies
        self.running_thread.start()

    def run(self):
        #snd_queue = self.snd_queue

        while self.running:

            # process send command
            if not self.snd_queue.empty():

                msg_id, msg = self.snd_queue.get()

                try:
                    self.send(msg_id, msg)
                except socket.timeout:
                    self.stdout("Timeout in sending, trying again...")
                    time.sleep(0.5)
                    self.send(msg_id, msg)

                except socket.error as e:
                    if e.errno == 10054 or e.errno == 10053:
                        self.stdout("Client has been disconnected.")
                        self.parent.close()
            try:
                self.read()
            except socket.timeout:
                pass # time outs are allowed
            except socket.error as e:
                if e.errno == socket.errno.WSAECONNRESET: # An existing connection was forcibly closed by the remote host
                    self.stdout("Is not available anymore.")
                    self.running = False

        self.parent.remove_client(self)
        self.socket.close()
        self.stdout("Closed.")


if __name__ == "__main__":
    pass
