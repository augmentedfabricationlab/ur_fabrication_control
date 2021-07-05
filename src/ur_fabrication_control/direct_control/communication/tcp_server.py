from __future__ import absolute_import
import time
import sys
import threading
if sys.version_info[0] == 2:
    import SocketServer as ss
elif sys.version_info[0] == 3:
    import socketserver as ss
from ..utilities.lists import isclose
ss.TCPServer.allow_reuse_address = True

__all__ = [
    'FeedbackHandler',
    'TCPFeedbackServer'
]

# def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
#     return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

class FeedbackHandler(ss.StreamRequestHandler):
    def handle(self):
        print("Connected to client at {}".format(self.client_address[0]))
        while True:
            data = self.rfile.readline().strip().decode('utf8')
            if not data:
                break
            self.server.rcv_msg.append(data)
            self.wfile.write(("Message from client: {}\n".format(data)).encode())

class TCPServer(ss.TCPServer):
    allow_reuse_address = True

class TCPFeedbackServer(object):
    def __init__(self, ip="192.168.10.11", port=50002, handler=FeedbackHandler):
        self.ip = ip
        self.port = port
        self.handler = handler

        self.server = TCPServer((self.ip, self.port), self.handler)
        self.server.rcv_msg = []
        self.msgs = {}

    def clear(self):
        self.server.rcv_msg = []
        self.msgs = {}

    def _create_thread(self):
        self.server_thread = threading.Thread(target=self.run)
        self.server_thread.daemon = True

    def shutdown(self):
        if hasattr(self, "server_thread"):
            self.server.shutdown()
            self.server_thread.join()
            del self.server_thread

    def start(self):
        self.shutdown()
        self._create_thread()
        self.server_thread.start()
        print("Server started in thread...")

    def run(self):
        try:
            self.server.serve_forever()
        except:
            pass

    def check_exit(self, exit_msg, tol=0.01):
        if exit_msg in self.msgs.values():
            return True
        elif any(isinstance(msg, list) for msg in self.msgs.values()) and isinstance(exit_msg, list):
            c = []
            for i, msg in enumerate(self.msgs.values()):
                if isinstance(msg,list) and len(msg) == len(exit_msg):
                    c.append(all(isclose(a, b, abs_tol=tol) for a,b in zip(msg, exit_msg)))
                else:
                    c.append(False)
            return any(c)
        else:
            return False

    def listen(self, exit_msg="Closing socket communication", tolerance=0.01, timeout=60):
        tCurrent = time.time()
        while not self.check_exit(exit_msg, tolerance):
            if self.server.rcv_msg is []:
                pass
            elif len(self.msgs) != len(self.server.rcv_msg):
                self.add_message(self.server.rcv_msg[len(self.msgs)])
            elif time.time() >= tCurrent + timeout:
                print("Listening to server timed out")
                return self.msgs
                break
        else:
            print("Exit message found: ", self.check_exit(exit_msg, tolerance))
            return self.msgs

    def add_message(self, msg):
        print("Adding message: {}".format(msg))
        if all(i in msg for i in ["[", "]", ","]):
            msg = msg.split('[', 1)[1].split(']')[0]
            msg = msg.split(',')
            msg = [eval(x) for x in msg]
        self.msgs[len(self.msgs)] = msg

if __name__ == '__main__':
    import socket
                
    address = ('localhost', 0) # let the kernel give us a port
    server = TCPFeedbackServer(ip=address[0], port=address[1], handler=FeedbackHandler)
    ip, port = server.server.server_address # find out what port we were given

    server.start()
    # Connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    # Send the data
    message = 'Hello, world\n'
    print('Sending : "%s"' % message)
    len_sent = s.send(message.encode())

    response = s.recv(1024).decode('utf8')
    print('Received: "%s"' % response)

    message = '[0.11,0.11,0.11,0.11,0.11,0.11]\n'
    print('Sending : "%s"' % message)
    len_sent = s.send(message.encode())

    response = s.recv(1024).decode('utf8')
    print('Received: "%s"' % response)


    message = 'Done\n'
    print('Sending : "%s"' % message)
    len_sent = s.send(message.encode())

    # Receive a response
    response = s.recv(1024).decode('utf8')
    print('Received: "%s"' % response)

    server.listen(exit_msg=[0.11,0.11,0.11,0.11,0.11,0.11], timeout=2)

    # Clean up
    s.close()
    print("socket closed")
    server.shutdown()
    print("Server is shut down")