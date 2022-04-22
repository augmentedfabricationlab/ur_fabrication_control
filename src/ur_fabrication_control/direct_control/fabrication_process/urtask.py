from fabrication_control import Task


class URTask(Task):
    def __init__(self):
        self.is_completed = False
        self.is_running = False
        self._stop_flag = True
        self.req_msg = None

    def set_server(self, server):
        self.server = server

    def set_urscript(self, urscript):
        self.urscript = urscript

    def set_req_msg(self, req_msg):
        self.req_msg = req_msg

    def wait_for_msg(self):
        while self.req_msg not in self.server.msgs.values():
            if self._stop_flag():
                break
        else:
            return True

    def run(self, _stop_flag):
        self._stop_flag = _stop_flag
        self.urscript.send_script()
        if self.wait_for_msg():
            self.is_completed = True
            return True
        if self._stop_flag():
            print("Task forced to stop")
            raise
