'''
Created on 20.09.2016

@author: rustr
'''

from threading import Thread
import socket
import struct
import time
import sys

if (sys.version_info > (3, 0)):
    from queue import Queue
else:
    from Queue import Queue


from ur_online_control.communication.msg_identifiers import *

class BaseClient(object):

    """ A simple client that is looping to receive some data, but it can also send data. """

    def __init__(self, identifier, host = "127.0.0.1", port = 30003):

        self.identifier = identifier
        self.host = host
        self.port = port
        self.byteorder = "!" # "!" network, ">" big-endian, "<" for little-endian, see http://docs.python.org/2/library/struct.html

        self.msg_rcv = ""

        self.snd_queue = Queue()
        self.rcv_queue = Queue()
        self.timeout = 0.008
        self.running = False

    def stdout(self, msg):
        msg = "%s: %s" % (self.identifier, str(msg))
        print(msg)

    def update(self):
        pass

    def run_inner_while(self):
        # GH does not like while loops. If we use this class in GH, we need to
        # call this function and update the component in order to have a while loop.

        # send
        try:
            while not self.snd_queue.empty():
                msg_id, msg = self.snd_queue.get_nowait()
                self._send(msg_id, msg)
        except socket.timeout:
            self.stdout("socket.timeout in sender.")
            self.close()
        except socket.error:
            self.stdout("socket.error in sender.")
            self.close()

        # read
        try:
            self.read()

        except socket.timeout as e:
            pass # recv timed out, retry ...

        except socket.error as e:
            if e.errno == 10004:
                # A blocking operation was interrupted by a call to WSACancelBlockingCall
                pass
            elif e.errno == 10035:
                # A non-blocking socket operation could not be completed immediately
                pass
            elif e.errno == 10022:
                # A request to send or receive data was disallowed because the ...
                pass
            else:
                self.stdout("socket.error in receiver: %s" % str(e))
                self.close()


    def run(self):
        while self.running:
            self.run_inner_while()
        self.socket.close()


    def start(self):
        self.running_thread = Thread(target = self.run)
        self.running_thread.daemon = False
        self.running_thread.start()

    def connect_to_server(self):
        self.running = False

        try:
            self.socket = socket.create_connection((self.host, self.port), timeout=self.timeout)
            self.socket.settimeout(self.timeout)
            self.socket.setblocking(0)
            self.send_id()
            self.stdout("Successfully connected to server %s on port %d." % (self.host, self.port))
            self.running = True
            return True

        except:
            self.stdout("Server %s is not available on port %d." % (self.host, self.port))
            self.running = False
            return False


    def send_id(self):
        msg = self.identifier
        self._send(MSG_IDENTIFIER, msg)

    def close(self):
        self.stdout("Closing...")
        self.running = False
        try:
            self.socket.close()
            self.running_thread.join()
            self.stdout("Successfully joined threads.")
        except:
            pass


    def send(self, msg_id, msg = None):
        self.snd_queue.put([msg_id, msg])

    def _format_other_messages(self, msg_id, msg = None):
        return None

    def _send(self, msg_id, msg = None):
        """ send message according to message id """

        buf = None

        if msg_id == MSG_FLOAT_LIST:
            msg_snd_len = struct.calcsize(str(len(msg)) + "f") + 4 # float array: length of message in bytes: len*4
            params = [msg_snd_len, msg_id] + msg
            buf = struct.pack(self.byteorder + "2i" + str(len(msg)) +  "f", *params)

        elif msg_id == MSG_IDENTIFIER:
            msg_snd_len = len(msg) + 4
            params = [msg_snd_len, msg_id, msg]
            buf = struct.pack(self.byteorder + "2i" + str(len(msg)) +  "s", *params)

        elif msg_id == MSG_STRING:
            msg_snd_len = len(msg) + 4
            params = [msg_snd_len, msg_id, msg]
            buf = struct.pack(self.byteorder + "2i" + str(len(msg)) +  "s", *params)

        elif msg_id == MSG_INT:
            msg_snd_len = 4 + 4
            params = [msg_snd_len, msg_id, msg]
            buf = struct.pack(self.byteorder + "3i", *params)

        elif msg_id == MSG_QUIT:
            msg_snd_len = 4
            params = [msg_snd_len, msg_id]
            buf = struct.pack(self.byteorder + "2i", *params)

        else:
            buf = self._format_other_messages(msg_id, msg)
            if not buf:
                self.stdout("Message identifier unknown: %d, message: %s" % (msg_id, msg))
                return

        self.socket.send(buf)
        self.stdout("Sent message %i with length %i." % (msg_id, len(buf)))


    def read(self):
        """ The transmission protocol for messages is
        [length msg in bytes] [msg identifier] [other bytes which will be read
        out according to msg identifier] """

        # read msg length
        self.msg_rcv += self.socket.recv(4)
        if len(self.msg_rcv) < 4:
            return

        msg_length = struct.unpack_from(self.byteorder + "i", self.msg_rcv, 0)[0]

        # read msg according to msg_length
        self.msg_rcv += self.socket.recv(msg_length)

        # read message identifier
        self.msg_rcv = self.msg_rcv[4:]
        msg_id = struct.unpack_from(self.byteorder + "i", self.msg_rcv[:4], 0)[0]

        raw_msg = self.msg_rcv[4:]

        # reset msg_rcv
        self.msg_rcv = ""

        # 4. pass message id and raw message to process method
        self.process(msg_length, msg_id, raw_msg)

        # 5. update
        self.update()

    def _process_other_messages(self, msg_len, msg_id, raw_msg):
        self.stdout("Message identifier unknown: %d, message: %s" % (msg_id, raw_msg))

    def process(self, msg_len, msg_id, raw_msg):

        msg = None

        if msg_id == MSG_QUIT:
            self.stdout("Received MSG_QUIT")
            self.close()
        elif msg_id == MSG_FLOAT_LIST:
            self.stdout("Received MSG_FLOAT_LIST")
            msg_float_tuple = struct.unpack_from(self.byteorder + str((msg_len-4)/4) + "f", raw_msg)
            msg_float_list = [item for item in msg_float_tuple]
            self.rcv_queue.put(msg_float_list)
        else:
            self._process_other_messages(msg_len, msg_id, raw_msg)

        return(msg_id, msg)

if __name__ == "__main__":

    import time
    ur = BaseClient("UR", "127.0.0.1", 30003)
    ur.connect_to_server()
    ur.start()
    ur.send(MSG_FLOAT_LIST, [-172.36, 442.80, 331.26, 2.8714, -1.2542, -0.0033])
    #ur.send(MSG_CURRENT_POSE_CARTESIAN, [-17236, 44280, 33126, 28714, -12542, -00033])
    time.sleep(5)
    #ur.send(MSG_CURRENT_POSE_CARTESIAN, [-10000, 100000, 100000, 28714, -12542, -00033])
    #ur.close()
