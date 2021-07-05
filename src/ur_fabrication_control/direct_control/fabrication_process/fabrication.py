import sys
from threading import Thread
from ..communication import TCPFeedbackServer
if sys.version_info[0] == 3:
    from queue import Queue
else:
    from Queue import Queue


class FabricationFeedbackServer(TCPFeedbackServer):
    def listen(self, stop, q):
        task_exit_msg = None
        while True:
            if stop():
                break
            if task_exit_msg is None and not q.empty():
                task_exit_msg = q.get()
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
        self.current_task = None

    def set_feedback_server(self, ip, port):
        self.server = FabricationFeedbackServer(ip, port)

    def add_task(self, task, exit_msg, key=None):
        if key is None:
            key = len(self.tasks)
        self.tasks[key] = {"state": "waiting",
                           "exit_message": exit_msg,
                           "task": task}

    def tasks_available(self):
        if len(self.tasks):
            for task in self.tasks.values():
                if task["state"] != "completed":
                    return True
            else:
                return False
        return False

    def get_next_task(self):
        keys = [key for key in self.tasks.keys()]
        keys.sort()
        for key in keys:
            if self.tasks[key]["state"] == "waiting":
                return key
        else:
            # No next task available
            return None

    def clear_tasks(self):
        self.tasks = {}

    def stop(self):
        self.perform_task(self.stop_task)
        self.close()

    def close(self):
        self._join_threads()
        self.server.clear()
        self.server.shutdown()

    def _join_threads(self):
        self._stop_thread = True
        if hasattr(self, "task_thread") and hasattr(self, "listen_thread"):
            self.task_thread.join()
            self.listen_thread.join()
            del self.task_thread
            del self.listen_thread

    def _create_threads(self):
        self._stop_thread = False
        self.q = Queue()
        self.task_thread = Thread(target=self.run,
                                  args=(lambda: self._stop_thread, self.q))
        self.listen_thread = Thread(target=self.server.listen,
                                    args=(lambda: self._stop_thread, self.q))
        self.task_thread.daemon = True
        self.listen_thread.daemon = True

    def start(self):
        self._join_threads()
        if self.tasks_available():
            self.server.start()
            self._create_threads()
            self.listen_thread.start()
            print("Started listening thread")
            self.task_thread.start()
            print("Started task thread")
        else:
            print("No_tasks_available")

    def run(self, stop_thread, q):
        while self.tasks_available():
            if stop_thread():
                self._performing_task = False
                break
            elif not self._performing_task:
                self.current_task = self.get_next_task()
                q.put(self.tasks[self.current_task]["exit_message"])
                self.perform_task(self.tasks[self.current_task]['task'])
                self._performing_task = True
            elif self._performing_task and not q.unfinished_tasks:
                q.join()
                print("joined task {}".format(self.current_task))
                self.tasks[self.current_task]["state"] = "completed"
                self._performing_task = False

    def perform_task(self, task):
        task.send_script()


if __name__ == '__main__':
    import socket
    import time

    ip, port = ('localhost', 67)
    # let the kernel give us a port

    class TestFabrication(Fabrication):
        def perform_task(self, task):
            self.s.send(task.encode())

    fab = TestFabrication()
    fab.stop_task = "All_done"
    fab.set_feedback_server(ip, port)
    fab.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fab.s.connect((ip, port))

    tasks = [
        "Task_1",
        "Task_2",
        "Task_3",
    ]

    [fab.add_task(task+"\n", task) for task in tasks]
    print(fab.tasks)
    fab_tasks_state = fab.tasks
    fab.start()
    time.sleep(2)
    fab.stop()
    print(fab.tasks)
    print(fab.server.msgs)

    # Send the data
    # message = 'Task_2_completed\n'
    # len_sent = s.send(message.encode())
    # print('Sending : "%s"' % message.strip())
    # Receive a response
    # response = s.recv(1024).decode('utf8')
    # print('Received: "%s"' % response.strip())

    # q = Queue()
    # q.put('Task_2_completed')
    # server_thread = Thread(target = server.listen, args=(lambda : stop, q))
    # server_thread.daemon = True
    # server_thread.start()
    # q.join()
    # print("Joined queue")
    # # Send the data
    # message = 'Task_2_completed\n'
    # len_sent = s.send(message.encode())
    # print('Sending : "%s"' % message.strip())
    # # Receive a response
    # response = s.recv(1024).decode('utf8')
    # print('Received: "%s"' % response.strip())

    # q.put('Task_2_completed')
    # q.join()
    # print("Joined queue AGAIN")

    # stop = True
    # server_thread.join()
    # print("Joined server")
    # # Clean up
    # s.close()
    # print("socket closed")
    # server.shutdown()
    # print("Server is shut down")
