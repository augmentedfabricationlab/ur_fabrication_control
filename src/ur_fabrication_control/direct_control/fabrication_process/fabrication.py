import sys, os
from queue import Queue
from threading import Thread
sys.path.append("C:/Users/Gido/Documents/workspace/development/ur_fabrication_control/src")
from ur_fabrication_control.direct_control.communication import TCPFeedbackServer, FeedbackHandler

class FabricationFeedbackServer(TCPFeedbackServer):
    def listen(self, stop, q):
        task_exit_msg = None
        while True:
            if stop():
                break
            if task_exit_msg == None and not q.empty():
                task_exit_msg = q.get(block=False)
            elif task_exit_msg in self.msgs.values():
                q.task_done()
                task_exit_msg = None
            if self.server.rcv_msg is []:
                pass
            elif len(self.msgs) != len(self.server.rcv_msg):
                self.add_message(self.server.rcv_msg[len(self.msgs)])

class Fabrication(object):
    def __init__(self):
        self.server = None
        self.tasks = {}
        self.stop_task = None
        self._stop_thread = False
        self._performing_task = False

        self.q = Queue()
        self.task_thread = Thread(target = self.run, args=(lambda : self._stop_thread, self.q))
        self.task_thread.daemon = True
    
    def set_feedback_server(self, ip, port):
        self.server = FabricationFeedbackServer(ip, port)
        self.server_thread = Thread(target = self.server.listen, args=(lambda : self._stop_thread, self.q))
        self.server_thread.daemon = True

    def add_task(self, task, exit_msg, key=None):
        if key == None:
            key = len(self.tasks)
        self.tasks[key] = {"state":"waiting", "exit_message":exit_msg, "task":task}

    def tasks_available(self):
        if len(self.tasks):
            for task in self.tasks.values():
                if task["state"] != "completed":
                    return True
            else:
                return False
        return False

    def get_next_task(self):
        keys = self.tasks.keys()
        keys.sort()
        for key in keys:
            if self.tasks[key]["state"]=="waiting":
                return key
        else:
            # No next task available
            return None

    def clear_tasks(self):
        self.tasks = {}

    def stop(self):
        self._stop_thread=True
        if self.task_thread.is_alive():
            self.task_thread.join()
        if self.server_thread.is_alive():
            self.server_thread.join()
        self.perform_task(self.stop_task)

    def start(self):
        if self.tasks_available():
            self._stop_thread=False
            self.task_thread.start()
            self.server_thread.start()
        else:
            print("No tasks available")

    def run(self, stop, q):
        while self.tasks_available():
            if stop():
                break
            elif not self._performing_task:
                self.current_task = self.get_next_task()
                q.put(self.tasks[self.current_task]["exit_message"])
                self.perform_task(self.tasks[self.current_task]["task"])
                self._performing_task = True
            try:
                q.join()
                self.tasks[self.current_task]["state"] = "completed"
                self._performing_task = False
            except:
                pass

    def perform_task(self, task):
        task.send_script()


if __name__ == '__main__':
    import socket
                
    address = ('localhost', 0) # let the kernel give us a port
    server = FabricationFeedbackServer(ip=address[0], port=address[1], handler=FeedbackHandler)
    ip, port = server.server.server_address # find out what port we were given
    stop = False
    server.start()
    # Connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    # Send the data
    message = 'Task_2_completed\n'
    len_sent = s.send(message.encode())
    print('Sending : "%s"' % message.strip())
    # Receive a response
    response = s.recv(1024).decode('utf8')
    print('Received: "%s"' % response.strip())

    q = Queue()
    q.put('Task_2_completed')
    server_thread = Thread(target = server.listen, args=(lambda : stop, q))
    server_thread.daemon = True
    server_thread.start()
    q.join()
    print("Joined queue")
    # Send the data
    message = 'Task_2_completed\n'
    len_sent = s.send(message.encode())
    print('Sending : "%s"' % message.strip())
    # Receive a response
    response = s.recv(1024).decode('utf8')
    print('Received: "%s"' % response.strip())

    q.put('Task_2_completed')
    q.join()
    print("Joined queue AGAIN")

    stop = True
    server_thread.join()
    print("Joined server")
    # Clean up
    s.close()
    print("socket closed")
    server.shutdown()
    print("Server is shut down")