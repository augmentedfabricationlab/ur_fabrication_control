if __name__ == "__main__":
    import sys, os
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../fabrication_manager/src'))
    print(src_path)
    sys.path.insert(0, src_path)
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    print(src_path)
    sys.path.insert(0, src_path)

from fabrication_manager.task import Task
from ur_fabrication_control.direct_control.communication.async_client import AsyncTCPClient
from ur_fabrication_control.direct_control import URScript
from ur_fabrication_control.direct_control.common import send_stop
import time
import logging
from multiprocessing import Event
import asyncio

__all__ = [
    "URTask"
]

class URTask(Task):
    def __init__(self, robot, robot_address, key=None, send_feedback=True, parallelizable=False):
        super(URTask, self).__init__(key=key, parallelizable=parallelizable)
        self.robot = robot
        self.robot_address = robot_address

        self.rec_msg = "Task_{}_received".format(key)
        self.req_msg = "Task_{}_complete".format(key)
        self.sent = False
        self.received = False
        # self.server = None
        self.server_name = "TCPFeedbackServer"
        self.server_address = None
        self.client = None
        self.send_feedback = send_feedback
        self.nodes = []
        self.urscript = None
        self.start_time = None

    @classmethod
    def from_urscript(cls, robot, robot_address, urscript, key=None):
        urtask = cls(robot, robot_address, key)
        urtask.urscript = urscript
        return urtask

    @classmethod
    def from_nodes(cls, robot, robot_address, nodes, key=None):
        urtask = cls(robot, robot_address, key)
        urtask.nodes = nodes
        return urtask

    def urscript_fabrication_header(self, results):
        ## Initialize instance
        self.urscript = URScript(*self.robot_address)
        self.urscript.start()
        
        if self.robot and self.robot.attached_tool:
            ## Set tool
            tool = self.robot.attached_tool
            self.urscript.set_tcp(list(tool.frame.point)+list(tool.frame.axis_angle_vector))
        self.urscript.textmessage(">> TASK {}".format(self.key), string=True)
        
        ## Establish communication
        # self.urscript.set_socket(*self.server.server.server_address, self.server.name)
        if self.send_feedback:
            self.urscript.set_socket(self.server_address[0], self.server_address[1], self.server_name)
            self.urscript.socket_open(self.server_name)
            ## Send script received msg
            self.urscript.socket_send_line_string(self.rec_msg, self.server_name)
        results.put("URTask {}: Fabrication header created".format(self.key))

    def urscript_fabrication_footer(self, results):
        if self.send_feedback:
            ## Send script finished msg
            self.urscript.socket_send_line_string(self.req_msg, self.server_name)
            self.urscript.socket_close(self.server_name)

        ## Add footer and generate script
        self.urscript.end()
        self.urscript.generate()   
        results.put("URTask {}: Fabrication footer created".format(self.key))

    def create_urscript_from_nodes(self, results):
        # currently assuming frames are in RCS
        for i, node in enumerate(self.nodes):
            if node.type == "linear":
                self.urscript.move_linear(node.frame, node.robot_vel, node.radius)
            elif node.type == "process":
                self.urscript.move_process(node.frame, node.robot_vel, node.radius)
            elif node.type == "joints":
                self.urscript.move_joint(node.joint_configuration, node.robot_vel)
            node_msg = {"TASK":self.key, "NODE":i}
            if self.send_feedback:
                self.urscript.socket_send_line_string(str(node_msg), self.server_name)
        results.put("URTask {}: URScript created from nodes".format(self.key))

    def create_urscript(self, results):
        if self.nodes:
            self.create_urscript_from_nodes(results)
        else:
            results.put("URTask {}: Using preconfigured URScript".format(self.key))

    def _create_urscript(self, results):
        self.urscript_fabrication_header(results)
        self.create_urscript(results)
        self.urscript_fabrication_footer(results)

    def work_func(self, results, interrupt_event):
        asyncio.run(self._work_func(results, interrupt_event))

    async def _work_func(self, results, interrupt_event, attempts=2):
        self.start_time = time.time()
        ## Create the urscript
        self._create_urscript(results)

        ## Send script with timeout and attempts clauses
        async with AsyncTCPClient(host='192.168.52.1', port=8888, confirmation_msg=self.rec_msg, completed_msg=self.req_msg) as client:
            timeout = time.time() + 10
            while not self.received:
                if not self.sent:
                    attempts -= 1
                    self.urscript.send_script()
                    results.put("URTask {}: URScript sent... attempts left {}".format(self.key, attempts))
                    results.put("client_confirmation: {} client_completed: {}".format(client.confirmation_received, client.completed_received))
                    self.sent = True
                    self.is_running = True
                if client and client.confirmation_received.is_set() and not self.received:
                    self.received = True
                    results.put("URTask {}: Received confirmation from UR".format(self.key))
                if not self.received and time.time() > timeout:
                    if attempts > 0:
                        self.sent = False
                        timeout = time.time() + 10
                    else:
                        results.put("URTask {}: FAULT - No attempts left, UR unreachable".format(self.key))
                        interrupt_event.set()
                        break
                if interrupt_event.is_set():
                    results.put("URTask {}: Forced to stop during send phase".format(self.key))
                    self.sent = False
                    self.is_running = False
                    self.is_completed = False
                    return
                await asyncio.sleep(0.1)

            ## Check if the script is finished or aborted
            while self.is_running and self.received:
                if client and client.completed_received.is_set():
                    results.put("URTask {}: Finished execution".format(self.key))
                    duration = time.time() - self.start_time
                    results.put("URTask {}: Duration {} s".format(self.key, duration))
                    self.is_running = False
                if interrupt_event.is_set():
                    results.put("URTask {}: Forced to stop during execution".format(self.key))
                    send_stop(self.urscript.ur_ip, self.urscript.ur_port)
                    self.sent = False
                    self.is_running = False
                    self.is_completed = False
                    return
                await asyncio.sleep(0.1)
            if self.received:
                self.is_completed = True
                results.put("URTask {}: Completed successfully".format(self.key))
            else:
                results.put("URTask {}: Failed to complete".format(self.key))

# Create a subclass to override script creation, if needed.
class URTask0(URTask):
    def create_urscript(self, results):
        self.urscript.textmessage("Running Task", string=True)
        self.urscript.add_sleep(1)
        results.put("URTask0: Custom script created")

if __name__ == "__main__":
    from multiprocessing import Queue, Event
    
    logs = []
    urtask = URTask0(None, ("192.168.52.128", 30002), key=0)
    urtask.send_feedback = True
    urtask.server_address = ("192.168.52.1", 8888)
    # urtask.server = server
    # For testing, print messages as they are produced.
    results = Queue()
    # Create an interrupt event for the task.
    intr_event = Event()
    # Build the script and run the UR work.
    urtask.start(results, interrupt_event=intr_event)
    print("URTask started.")
    urtask.join()
    print("URTask joined.")
    
    while True:
        try:
            msg = results.get_nowait()
            print("LOG:", msg)
            logs.append(msg)
        except Exception:
            break