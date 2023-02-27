from fabrication_manager.task import Task
from ur_fabrication_control.direct_control import URScript
from ur_fabrication_control.direct_control.common import send_stop

__all__ = [
    "URTask"
]

class URTask(Task):
    def __init__(self, robot, robot_address, key=None):
        super(URTask, self).__init__(key)
        self.robot = robot
        self.robot_address = robot_address
        self.req_msg = "Task_{}_complete".format(key)
        self.sent = False
        self.server = None

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

    def create_urscript_from_nodes(self, nodes):
        self.urscript = URScript(*self.robot_address)
        self.urscript.start()
        tool = self.robot.attached_tool
        self.urscript.set_tcp(list(tool.frame.point)+list(tool.frame.axis_angle_vector))
        self.urscript.add_line("textmsg(\">> TASK{}.\")".format(self.key))
        
        # Find a way to replace the socket open command with recent server ip an port
        self.urscript.socket_open(self.server.ip, self.server.port, self.server.name)

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
        
        self.urscript.socket_send_line_string(self.req_msg, self.server.name)
        self.urscript.socket_close()

        self.urscript.end()
        self.urscript.generate()

    def check_req_msg(self):
        self.log("req_msg" + self.req_msg)
        self.log("values" + str(self.server.msgs.values()))
        return self.req_msg in self.server.msgs.values()

    def run(self, stop_thread):
        if not self.sent:
            self.urscript.send_script()
            self.log("URScript sent...")
            self.sent = True
        while not self.check_req_msg():
            if stop_thread():
                self.log("Forced to stop...")
                send_stop(self.urscript.ur_ip, self.urscript.ur_port)
                self.sent = False
                self.is_running = False
                self.is_completed = False
                break
            else:
                pass
        else:
            self.is_completed = True
            return True