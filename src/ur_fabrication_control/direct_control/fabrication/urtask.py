from fabrication_manager.task import Task
from ur_fabrication_control.direct_control import URScript
from ur_fabrication_control.direct_control.common import send_stop
import time

__all__ = [
    "URTask"
]

class URTask(Task):
    def __init__(self, robot, robot_address, key=None):
        super(URTask, self).__init__(key)
        self.robot = robot
        self.robot_address = robot_address
        self.rec_msg = "Task_{}_received".format(key)
        self.req_msg = "Task_{}_complete".format(key)
        self.sent = False
        self.received = False
        self.server = None
        self.nodes = []

    @classmethod
    def from_urscript(cls, robot, robot_address, urscript, key=None):
        urtask = cls(robot, robot_address, key)
        urtask.urscript = urscript
        return urtask

    @classmethod
    def from_nodes(cls, robot, robot_address, nodes, key=None):
        urtask = cls(robot, robot_address, key)
        urtask.create_urscript_from_nodes(nodes)
        return urtask

    def urscript_fabrication_header(self):
        ## Initialize instance
        self.urscript = URScript(*self.robot_address)
        self.urscript.start()
        
        if self.robot:
            ## Set tool
            tool = self.robot.attached_tool
            self.urscript.set_tcp(list(tool.frame.point)+list(tool.frame.axis_angle_vector))
        self.urscript.textmessage(">> TASK{}".format(self.key), string=True)
        
        ## Establish communication
        # self.urscript.set_socket(*self.server.server.server_address, self.server.name)
        self.urscript.set_socket(self.server.ip, self.server.port, self.server.name)
        self.urscript.socket_open(self.server.name)
        ## Send script received msg
        self.urscript.socket_send_line_string(self.rec_msg, self.server.name)

    def urscript_fabrication_footer(self):
        ## Send script finished msg
        self.urscript.socket_send_line_string(self.req_msg, self.server.name)
        self.urscript.socket_close(self.server.name)

        ## Add footer and generate script
        self.urscript.end()
        self.urscript.generate()   

    def create_urscript_from_nodes(self, nodes):
        # currently assuming frames are in RCS
        for i, node in enumerate(nodes):
            if node.type == "linear":
                self.urscript.move_linear(node.frame, node.robot_vel, node.radius)
            elif node.type == "process":
                self.urscript.move_process(node.frame, node.robot_vel, node.radius)
            elif node.type == "joints":
                self.urscript.move_joint(node.joint_configuration, node.robot_vel)
            node_msg = {"TASK":self.key, "NODE":i}
            self.urscript.socket_send_line_string(str(node_msg), self.server.name)

    def create_urscript(self):
        self.create_urscript_from_nodes(self.nodes)

    def _create_urscript(self):
        self.urscript_fabrication_header()
        self.create_urscript()
        self.urscript_fabrication_footer()

    def check_msg(self, msg):
        return msg in self.server.msgs.values()

    def run(self, stop_thread, attempts=2):
        ## Create the urscript
        self._create_urscript()

        ## Send script with timeout and attempts clauses
        timeout = time.time() + 10
        while not self.received:
            if not self.sent:
                attempts -= 1
                self.urscript.send_script()
                self.log("URScript sent... attempts left {}".format(attempts))
                self.sent = True
                self.is_running = True
            if self.check_msg(self.rec_msg) and not self.received:
                self.received = True
            if not self.received and time.time() > timeout:
                if attempts > 0:
                    self.sent = False
                    timeout = time.time() + 10
                else:
                    self.log("FAULT... No attempts left... UR could not be reached")
                    break
            if stop_thread():
                self.log("Forced to stop...")
                self.sent = False
                self.is_running = False
                self.is_completed = False
                break
        
        ## Check if the script is finished or aborted
        while self.is_running and self.received:
            if self.check_msg(self.req_msg):
                self.log("Finished")
                self.is_running = False
            if stop_thread():
                self.log("Forced to stop...")
                send_stop(self.urscript.ur_ip, self.urscript.ur_port)
                self.sent = False
                self.is_running = False
                self.is_completed = False
                break
        else:
            self.is_completed = True
            return True

if __name__ == "__main__":
    from ur_fabrication_control.direct_control.communication import TCPFeedbackServer
    class URTask0(URTask):
        def create_urscript(self):
            self.urscript.textmessage("Running Task", string=True)
    
    with TCPFeedbackServer("192.168.0.42", 50015) as server:
        urtask = URTask0(None, ("192.168.0.210", 30002), key=0)
        urtask.server = server
        urtask._create_urscript()
        # print(urtask.urscript.script)
        urtask.run(lambda:False)
        print(server.msgs)
        time.sleep(2)
    print(urtask.log_messages)