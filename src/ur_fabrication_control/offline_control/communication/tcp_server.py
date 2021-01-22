from __future__ import absolute_import
import time
import sys
import threading
if sys.version_info[0] == 2:
    import SocketServer as ss
elif sys.version_info[0] == 3:
    import socketserver as ss
from utilities.lists import isclose
ss.TCPServer.allow_reuse_address = True

__all__ = [
    'FeedbackHandler',
    'TCPFeedbackServer'
]


class FeedbackHandler(ss.StreamRequestHandler):
    def handle(self):
        data = self.rfile.readlines()
        data = [line.strip() for line in data]
        self.server.rcv_msg.append(data)


class TCPServer(ss.TCPServer):
    allow_reuse_address = True

class TCPFeedbackServer:
    def __init__(self, ip="192.168.10.11", port=50002, handler=FeedbackHandler):
        self.ip = ip
        self.port = port
        self.handler = handler

        self.reset()
        self.msgs = {}
        self.log_messages = []
        self.log_messages_length = 25

    def reset(self):
        self.server = TCPServer((self.ip, self.port), self.handler)
        self.server.rcv_msg = []
        self.t = threading.Thread(target=self.server.serve_forever)
        self.t.daemon = True

    def get(self):
        return self.server

    def start(self):
        self.t.start()
        print("Server running...")

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    def join(self):
        self.t.join()

    def is_alive(self):
        return self.t.is_alive()

    def check_exit(self, exit_msg, tol):
        if "Done" in self.msgs.values():
            return True
        elif len(self.msgs) == self.check_msgs:
            return False
        else:
            msg = self.msgs[self.check_msgs]
            self.check_msgs += 1
            if type(msg) == list and type(exit_msg) == list:
                return all(isclose(msg[i], exit_msg[i], abs_tol=tol) for i in range(len(msg)))
            elif msg == exit_msg or msg == 'Done':
                return True

    def listen(self, exit_msg="Done", tolerance=25, timeout=60):
        self.check_msgs = 0
        tCurrent = time.time()
        while not self.check_exit(exit_msg, tolerance):
            if self.server.rcv_msg is None:
                pass
            elif type(self.server.rcv_msg) != list and len(self.msgs) < 1:
                self.add_message(self.server.rcv_msg)
            elif type(self.server.rcv_msg) == list and len(self.msgs) < len(self.server.rcv_msg):
                if len(self.msgs) is None:
                    ind = 0
                else:
                    ind = len(self.msgs)
                self.add_message(self.server.rcv_msg[ind][0])
            elif time.time() >= tCurrent + timeout:
                break
        else:
            return True

    def add_message(self, msg):
        i = len(self.msgs)
        msg = msg.decode('utf-8')
        if "[" in msg and "]" in msg:
            msg = msg.split('[', 1)[1].split(']')[0]
        if "," in msg:
            msg = msg.split(',')
        self.msgs[i] = msg
        self.log(msg)

    def log(self, msg):
        self.log_messages.append("SERVER: " + str(msg))
        if len(self.log_messages) > self.log_messages_length:
            self.log_messages = self.log_messages[-self.log_messages_length:]

    def get_log_messages(self):
        return "\n".join(self.log_messages)

