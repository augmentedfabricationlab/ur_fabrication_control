'''
Created on 22.09.2016

@author: rustr
'''

import struct
import sys
from .base_client_socket import *

if (sys.version_info > (3, 0)):
    from queue import LifoQueue
else:
    from Queue import LifoQueue

from ur_online_control.communication.states import *

class ActuatorSocket(BaseClientSocket):

    """ The ActuatorSocket extends, respectively differs from the ClientSocket in a few points:
    1. The actuator can just handle a specific size of commands at once, so it  must be set
       in packets to a specific length ( = stack_size)
    2. The actuator can be in different states: READY_TO_PROGRAM, EXECUTING and READY_TO_RECEIVE.
    3. If the ActuatorSocket has sent all messages on the stack, and also received the same
       amount of messages, it will go into READY_TO_PROGRAM state.
    """

    def __init__(self, socket, ip, parent):

        super(ActuatorSocket, self).__init__(socket, ip, parent)

        self.state = READY_TO_PROGRAM

        self.stack_size = 5
        self.stack = []
        self.stack_counter = 0

        self.command_counter = 0
        self.command_counter_executed = 0

        # state publishing
        self.queue_timeout = 1.
        self.current_pose_cartesian_queue = LifoQueue()
        self.current_pose_joints_queue = LifoQueue()
        self.current_digital_in_queue = LifoQueue()
        self.current_analog_in_queue = LifoQueue()


    def reset_counters(self):
        if self.state == READY_TO_PROGRAM:
            self.command_counter = 0
            self.command_counter_executed = 0
            container.CONNECTED_CLIENTS.put(self.identifier, [self.state, self.command_counter_executed])
        else:
            self.stdout("reset_counters: state is not READY_TO_PROGRAM ")

    def update(self):
        container.CONNECTED_CLIENTS.put(self.identifier, [self.state, self.command_counter_executed])

    def send_command(self, msg_id, msg):
        """ Puts the message on the stack and calls handle_stack """
        self.stack.append([msg_id, msg])
        self.handle_stack()
    
    def _send_command(self, cmd):
        msg_id, msg = cmd
        buf = self._format_command(msg_id, msg)
        self.socket.send(buf)

    def _format_command(self, msg_id, msg):
        pass

    def empty_stack(self):
        self.stack = []

    def get_stack_length(self):
        return len(self.stack)

    def handle_stack(self, msg_counter = None):
        if not len(self.stack) and self.stack_counter == 0:
            if msg_counter == self.command_counter:
                # The actuator is ready to be programmed
                self.state = READY_TO_PROGRAM
                self.reset_counters()
                self.stdout("Set state to READY_TO_PROGRAM")
                self.update()

        elif len(self.stack) and self.stack_counter == 0 :
            # The actuator is ready to be programmed, and receives first packet from the stack
            for i in range(min(self.stack_size, len(self.stack))):
                cmd = self.stack.pop(0)
                self.command_counter += 1
                self.state = EXECUTING
                self._send_command(cmd)
                self.stack_counter -= 1

        elif len(self.stack) and -self.stack_size <= self.stack_counter and self.stack_counter < 0 :
            # The actuator is currently executing, but ready to receive another packet from the stack
            try:
                cmd = self.stack.pop(0)
                self.command_counter += 1
                self.state = EXECUTING
                self._send_command(cmd)
                self.stack_counter -= 1

            except IndexError: # does happen sometimes: not thread-safe ??
                pass
        else:
            # The actuator must still accomplish some commands and return them
            pass


    def publish_queues(self):
        super(ActuatorSocket, self).publish_queues()
        container.RCV_QUEUES.put(self.identifier, {MSG_CURRENT_POSE_CARTESIAN: self.current_pose_cartesian_queue})
        container.RCV_QUEUES.put(self.identifier, {MSG_CURRENT_POSE_JOINT: self.current_pose_joints_queue})
        container.RCV_QUEUES.put(self.identifier, {MSG_CURRENT_DIGITAL_IN: self.current_digital_in_queue})
        container.RCV_QUEUES.put(self.identifier, {MSG_CURRENT_ANALOG_IN: self.current_analog_in_queue})

    def _process_other_messages(self, msg_len, msg_id, raw_msg):

        #self.stdout("Received %i" % msg_id)

        if msg_id == MSG_COMMAND_RECEIVED:
            msg_counter = struct.unpack_from(self.byteorder + "i", raw_msg)[0]
            self._process_msg_cmd_received(msg_counter)

        elif msg_id == MSG_COMMAND_EXECUTED:
            msg_counter = struct.unpack_from(self.byteorder + "i", raw_msg)[0]
            self._process_msg_cmd_executed(msg_counter)

        elif msg_id == MSG_CURRENT_POSE_CARTESIAN:
            current_pose_cartesian = self._format_current_pose_cartesian(raw_msg)
            self._process_current_pose_cartesian(current_pose_cartesian)

        elif msg_id == MSG_CURRENT_POSE_JOINT:
            current_pose_joint = self._format_current_pose_joint(raw_msg)
            self._process_current_pose_joint(current_pose_joint)

        elif msg_id == MSG_CURRENT_DIGITAL_IN:
            current_digital_in = self._format_current_digital_in(msg_len, raw_msg)
            self._process_current_digital_in(current_digital_in)
        
        elif msg_id == MSG_CURRENT_ANALOG_IN:
            current_analog_in = self._format_current_analog_in(msg_len, raw_msg)
            self._process_current_analog_in(current_analog_in)

        else:
            self.stdout("msg_id %d" % msg_id)
            self.stdout("Message identifier unknown:  %d, message: %s" % (msg_id, raw_msg))

    def _process_msg_cmd_received(self, msg_counter):
        self.state = READY_TO_RECEIVE
        self.stack_counter += 1
        #self.handle_stack()

    def _process_msg_cmd_executed(self, msg_counter):
        self.command_counter_executed = msg_counter
        self.update()
        self.handle_stack(msg_counter)

    def _format_other_messages(self, msg_id, msg):
        buf = None

        if msg_id in [MSG_CURRENT_POSE_CARTESIAN, MSG_CURRENT_POSE_JOINT]:
            msg_snd_len = 4
            params = [msg_snd_len, msg_id]
            buf = struct.pack(self.byteorder + "%ii" % len(params), *params)

        elif msg_id == MSG_DIGITAL_IN:
            msg_snd_len = 4 + 4
            params = [msg_snd_len, msg_id, int(msg)]
            buf = struct.pack(self.byteorder + "%ii" % len(params), *params)
        
        elif msg_id == MSG_ANALOG_IN:
            msg_snd_len = 4 + 4
            params = [msg_snd_len, msg_id, int(msg)]
            buf = struct.pack(self.byteorder + "%ii" % len(params), *params)

        elif msg_id == MSG_COMMAND:
            buf = self._format_command(msg_id, msg)

        elif msg_id == MSG_SPEED:
            buf = self._format_speed(msg_id, msg)
        
        elif msg_id == MSG_TCP:
            buf = self._format_tcp(msg_id, msg)
            
        elif msg_id == MSG_POPUP:
            msg_snd_len = 4
            params = [msg_snd_len, msg_id]
            buf = struct.pack(self.byteorder + "2i", *params)

        return buf

    def _format_current_pose_cartesian(self, raw_msg):
        pass

    def _format_current_pose_joint(self, raw_msg):
        pass

    def _format_current_digital_in(self, msg_len, raw_msg):
        pass

    def _format_current_analog_in(self, msg_len, raw_msg):
        pass

    def _format_speed(self, msg_id, msg):
        pass
    
    def _format_tcp(self, msg_id, msg):
        pass

    def _process_current_pose_cartesian(self, current_pose_cartesian):
        pass

    def _process_current_pose_joint(self, current_pose_joint):
        pass

    def _process_current_digital_in(self, digital_in):
        pass

    def _process_current_analog_in(self, analog_in):
        pass

    def get_from_queue(self, queue):
        """ Returns success, value(s). """
        try:
            if not queue.empty():
                value = queue.get(timeout=self.queue_timeout)
                return True, value
            else:
                self.stdout("Queue: %s empty." % str(queue))
                return False, None
        except: # timeout error??
            return False, None

    def get_current_pose_cartesian(self):
        #self.socket.send(MSG_CURRENT_POSE_CARTESIAN)
        return self.get_from_queue(self.current_pose_cartesian_queue)

    def get_current_pose_joints(self):
        ok, value = self.get_from_queue(self.current_pose_joints_queue)
        return ok, value

    def get_current_digital_in(self):
        return self.get_from_queue(self.current_digital_in_queue)
    
    def get_current_analog_in(self):
        return self.get_from_queue(self.current_analog_in_queue)


class URSocket(ActuatorSocket):

    #MULT = 100000.0 # for converting the integers to floats #py2.7
    MULT = 100000 # for converting the integers to floats 

    def __init__(self, socket, ip, parent):
        super(URSocket, self).__init__(socket, ip, parent)

        self.stack_size = 5
        self.byteorder = "!"
    
    def update(self):
        """This method is called on READY_TO_PROGRAM and MSG_COUNTER_EXECUTED.
        """
        super(URSocket, self).update()
        

    def _format_command(self, msg_id, msg):
        """
        MSG_COMMAND = 1 # [counter, position, orientation, optional values]
        called from handle stack: individual commands have to created for the specific actuator socket.
        UR: [x, y, z, ax, ay, az, acc, speed, radius, time]
        """

        command_id, cmd = msg

        if command_id in [COMMAND_ID_MOVEL, COMMAND_ID_MOVEJ]:
            msg_command_length = 4 * (len(cmd) + 1 + 1 + 1) # + msg_id, command_id, command_counter
            cmd = [c * self.MULT for c in cmd]
            params = [msg_command_length, msg_id, command_id, self.command_counter] + cmd
        
        elif command_id == COMMAND_ID_MOVEC:
            raise NotImplementedError("")
        
        elif command_id == COMMAND_ID_MOVEP:
            raise NotImplementedError("")
        
        elif command_id == COMMAND_ID_DIGITAL_OUT:
            msg_command_length = 4 * (len(cmd) + 1 + 1 + 1) # + msg_id, command_id, command_counter
            params = [msg_command_length, msg_id, command_id, self.command_counter] + cmd

        elif command_id == COMMAND_ID_WAIT:
            msg_command_length = 4 * (len(cmd) + 1 + 1 + 1)
            cmd = [c * self.MULT for c in cmd]
            params = [msg_command_length, msg_id, command_id, self.command_counter] + cmd
        
        elif command_id == COMMAND_ID_TCP:
            msg_command_length = 4 * (len(cmd) + 1 + 1 + 1)
            cmd = [c * self.MULT for c in cmd]
            params = [msg_command_length, msg_id, command_id, self.command_counter] + cmd
            
        elif command_id == COMMAND_ID_POPUP:
            msg_command_length = 4 * (1 + 1 + 1)
            params = [msg_command_length, msg_id, command_id, self.command_counter]
        
        else:
            raise("command_id unknown.")

        buf = struct.pack(self.byteorder + "%ii" % len(params), *params)
        return buf

    def _format_speed(self, msg_id, speed):
        msg_command_length = 4 * 2
        speed *= self.MULT
        params = [msg_command_length, msg_id, speed]
        buf = struct.pack(self.byteorder + "%ii" % len(params), *params)
        return buf
    
    def _format_tcp(self, msg_id, msg):
        msg_command_length = 4 * (len(msg) + 1)
        msg = [c * self.MULT for c in msg]
        params = [msg_command_length, msg_id] + msg
        buf = struct.pack(self.byteorder + "%ii" % len(params), *params)
        return buf

    def _format_current_pose_cartesian(self, raw_msg):
        ''' MSG_CURRENT_POSE_CARTESIAN = 5 # [position, orientation] '''
        current_pose_cartesian_tuple = struct.unpack_from(self.byteorder + "%ii" % (6), raw_msg)
        current_pose_cartesian = [s / self.MULT for s in current_pose_cartesian_tuple]
        return current_pose_cartesian

    def _format_current_pose_joint(self, raw_msg):
        ''' MSG_CURRENT_POSE_JOINT = 5 # [j1, j2, j3, j4, j5, j6] '''
        current_pose_joint_tuple = struct.unpack_from(self.byteorder + "%ii" % (6), raw_msg)
        current_pose_joint = [s / self.MULT for s in current_pose_joint_tuple]
        return current_pose_joint

    def _format_current_digital_in(self, msg_len, raw_msg):
        di_num = (msg_len - 4)/4
        current_digital_in = struct.unpack_from(self.byteorder + "%ii" % (di_num), raw_msg)
        # make number, value pairs
        current_digital_in = [[current_digital_in[i], current_digital_in[i+1]] for i in range(0, len(current_digital_in), 2)]
        return current_digital_in
    
    def _format_current_analog_in(self, msg_len, raw_msg):
        di_num = (msg_len - 4)/4
        current_analog_in = struct.unpack_from(self.byteorder + "%ii" % (di_num), raw_msg)
        # make number, value pairs
        current_analog_in = [[current_analog_in[i], current_analog_in[i+1] / self.MULT] for i in range(0, len(current_analog_in), 2)]
        return current_analog_in

    def _process_current_pose_cartesian(self, current_pose_cartesian):
        self.current_pose_cartesian_queue.put(current_pose_cartesian)

    def _process_current_pose_joint(self, current_pose_joint):
        self.current_pose_joints_queue.put(current_pose_joint)

    def _process_current_digital_in(self, current_digital_in):
        self.current_digital_in_queue.put(current_digital_in)
    
    def _process_current_analog_in(self, current_analog_in):
        self.current_analog_in_queue.put(current_analog_in)
