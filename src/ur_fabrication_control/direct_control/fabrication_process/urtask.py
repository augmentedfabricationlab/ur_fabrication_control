from fabrication_control.task import Task


class URTask(Task):
    def __init__(self, server, urscript, req_msg, key=None):
        super(URTask, self).__init__(key)
        self.req_msg = None
        self.server = server
        self.urscript = urscript
        self.req_msg = req_msg
        self.sent = False

    def check_req_msg(self):
        return self.req_msg in self.server.msgs.values()

    def run(self, stop_thread):
        if not self.sent:
            self.urscript.send_script()
            self.log("URScript sent...")
            self.sent = True
        while not self.check_req_msg():    
            if stop_thread():
                self.log("Forced to stop...")
                print("breaking loop")
                break
            else:
                pass
        else:
            self.is_completed = True
            return True

