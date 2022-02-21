import os
import socket
from compas.geometry import Line
from .communication import URSocketComm
from .utilities import islist

__all__ = [
    'URScript'
]


class URScript(URSocketComm):
    """Class to build a script of commands for the UR Robot system.

    Parameters
    ----------
    ur_ip : string (None)
        IP of the UR Robot.
    ur_port : integer (None)
        Port number of the UR Robot.

    Attributes
    ----------
    commands_dict (read-only) : dictionary
        A dictionary to store the command lines.
    ur_ip : string
        IP of the UR Robot.
    ur_port : integer
        Port number of the UR Robot.
    script (read-only) : string
        A string generated from the commands_dict to be sent to the UR Robot.

    """
    def __init__(self, ur_ip=None, ur_port=None):
        self.commands_dict = {}
        self.ur_ip = ur_ip
        self.ur_port = ur_port
        self.script = None
        self.sockets = {}
        self.var_names = []

        # Functionality
    def start(self):
        """Build the start of the script.

        Parameters
        ----------
        None

        Returns
        -------
        None
            The start line is added to the command dictionary.

        """
        self.add_lines(["def program():",
                        "\ttextmsg(\">> Entering program.\")",
                        "\t# open line for airpick commands"], indent=0)

    def end(self):
        """Build the end of the script.

        Parameters
        ----------
        None

        Returns
        -------
        None
            The end line is added to the command dictionary.

        """
        if self.sockets != {}:
            for socket_name in self.sockets.keys():
                sock_msg = "Socket with name: {} and address {} was not closed"
                print(sock_msg.format(socket_name, self.sockets[socket_name]))
                self.socket_close(socket_name)
                print("Socket has been closed at program end")
        self.add_lines(["\ttextmsg(\"<< Exiting program.\")",
                        "end",
                        "program()\n\n\n"], indent=0)

    def generate(self):
        """Translate the script from a dictionary to a long string.

        Parameters
        ----------
        None

        Returns
        -------
        script : string
            A long string generated from the command dictionary.

        """
        self.script = '\n'.join(self.commands_dict.values())
        return self.script

    # Dictionary building
    def add_line(self, line, i=None, indent=1):
        """Add a single line to the script.

        Parameters
        ----------
        line : string
            A single command line.

        Returns
        -------
        None
            A single line added to the command dictionary.

        """
        if i is None:
            i = len(self.commands_dict)
        else:
            pass
        self.commands_dict[i] = "\t"*indent+line
        return line

    def add_lines(self, lines, indent=1):
        """Add multiple lines to the script.

        Parameters
        ----------
        lines : sequence of string
            A list of command lines.

        Returns
        -------
        None
            Multiple lines added to the command dictionary.

        """
        i = len(self.commands_dict)
        for (ind, line) in enumerate(lines):
            self.add_line(line, i+ind, indent)
        return lines

    # Feedback functionality
    def get_current_pose_cartesian(self, socket_name="socket_0",
                                   address=("192.168.10.11", 50002),
                                   send=False):
        """Get the current cartesian pose.

        Parameters
        ----------
        send : boolean
            Set to "True" to send current pose from UR Robot to server.
            Default set to "False" to only print out on UR Robot display.

        Returns
        -------
        None

        """
        self.get_current_pose("cartesian", socket_name, address, send)

    def get_current_pose_joints(self, socket_name="socket_0",
                                address=("192.168.10.11", 50002),
                                send=False):
        """Get the current joint positions.

        Parameters
        ----------
        send : boolean
            Set to "True" to send current pose from UR Robot to server.
            Default set to "False" to only print out on UR Robot display.

        Returns
        -------
        None

        """
        self.get_current_pose("joints", socket_name, address, send)

    def get_current_pose(self, get_type, socket_name="socket_0",
                         address=("192.168.10.11", 50002), send=False):
        """Create get pose code.

        """
        pose_type = {"cartesian": "get_forward_kin()",
                     "joints": "get_actual_joint_positions()"}
        func = "current_pose = {}".format(pose_type[get_type])
        self.add_lines([func, "textmsg(current_pose)"])
        if send:
            self.socket_send_line('current_pose\n', socket_name, address)
        return func

    def textmessage(self, message, string=False):
        if string:
            line = 'textmsg("{}")'.format(message)
        else:
            line = 'textmsg({})'.format(message)
        return self.add_line(line)

    # Connectivity
    def is_available(self):
        """Ping the UR network to check for availability.

        Parameters
        ----------
        None

        Returns
        -------
        boolean
            "True" if available.
            "False" if unavailable.

        """
        system_call = "ping -r 1 -n 1 {}".format(self.ur_ip)
        response = os.system(system_call)
        if response == 0:
            return True
        else:
            return False

    def send_script(self):
        """Send the generated script to the UR Robot.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        try:
            s = socket.create_connection((self.ur_ip, self.ur_port), timeout=2)
        except socket.timeout:
            addr_msg = "UR with ip {} not available on port {}"
            print(addr_msg.format(self.ur_ip, self.ur_port))
            raise ConnectionError
        finally:
            enc_script = self.script.encode('utf-8')
            # encoding allows use of python 3.7
            s.send(enc_script)
            sent_msg = "Script sent to {} on port {}"
            print(sent_msg.format(self.ur_ip, self.ur_port))
            s.close()

    # Geometric effects
    def set_tcp(self, tcp):
        """Set the tcp (tool center point) in the script.

        Parameters
        ----------
        tcp : sequence of float
            Tool center point in a form of list.
            tcp = [x, y, z, dx, dy, dz]

        Returns
        -------
        None
            The tcp is set in the command dictionary.

        """
        # tcp = [tcp[i]/1000 if i < 3 else tcp[i] for i in range(len(tcp))]
        tcp = [tcp[i] for i in range(len(tcp))]
        return self.add_line("set_tcp(p{})".format(tcp))

    def move_linear(self, frame, velocity=0.05, radius=0):
        """Add a move linear command to the script.

        Parameters
        ----------
        move_command : sequence of float
            List of x, y, z position, dx, dy, dz axis, velocity and radius.
            move_command = [x, y, z, dx, dy, dz, v, r]

        Returns
        -------
        None
            A move linear command is added to the command dictionary.

        """
        pose = self._frame_to_pose(frame)
        return self.add_line("movel({}, v={}, r={})".format(pose, velocity,
                                                            radius))

    def moves_linear(self, frames, velocity=0.05, max_radius=0.1):
        # Multiple moves, can calculate the radius
        kwargs_dict = {self._get_var_name("poses"):
                       self._frames_to_poses(frames),
                       self._get_var_name("radii"):
                       self._radii_between_frames(frames, max_radius),
                       "velocity": velocity}
        func = "movel({1}[i], v={0}, r={2}[i])".format(kwargs_dict["velocity"],
                                                       kwargs_dict.keys()[0],
                                                       kwargs_dict.keys()[1])
        return self._while_move_wrapper(func, **kwargs_dict)

    def move_joint(self, joint_configuration, velocity):
        """Add a move joint command to the script.

        Parameters
        ----------
        joint_configuration : object
            compas_fab.robots.Configuration

        velocity : float
            Velocity of the joint.

        Returns
        -------
        None
            A move joint command is added to the command dictionary.

        """
        return self.add_line("movej({}, v={})".format(
                             joint_configuration.joint_values, velocity))

    def moves_joint(self, joint_configurations, velocity):
        # multiple joint positions
        kwargs_dict = {self._get_var_name("joint_values"):
                       [j.joint_values for j in joint_configurations],
                       'velocity': velocity}
        func = "movej({1}[i], v={0})".format(kwargs_dict['velocity'],
                                             kwargs_dict.keys()[0])
        return self._while_move_wrapper(func, **kwargs_dict)

    def move_process(self, frame, velocity, radius):
        """Add a move process command to the script.

        Parameters
        ----------
        move_command : sequence of float
            List of x, y, z position, dx, dy, dz axis, velocity and radius.
            move_command = [x, y, z, dx, dy, dz, v, r]

        Returns
        -------
        None
            A move linear command is added to the command dictionary.

        """
        pose = self._frame_to_pose(frame)
        return self.add_line("movep({}, v={}, r={})".format(pose, velocity,
                                                            radius))

    def moves_process(self, frames, velocity=0.05, max_radius=0):
        # multiple moves, can calculate the radius
        kwargs_dict = {self._get_var_name("poses"):
                       self._frames_to_poses(frames),
                       self._get_var_name("radii"):
                       self._radii_between_frames(frames, max_radius),
                       "velocity": velocity}
        func = "movep({1}[i], v={0}, r={2}[i])".format(kwargs_dict["velocity"],
                                                       kwargs_dict.keys()[0],
                                                       kwargs_dict.keys()[1])
        return self._while_move_wrapper(func, **kwargs_dict)

    def move_circular(self, frame_via, frame_to, velocity, radius):
        """
        """
        pose_via = self._frame_to_pose(frame_via)
        pose_to = self._frame_to_pose(frame_to)
        return self.add_line("movec({}, {}, v={}, r={})".format(
                                pose_via, pose_to, velocity, radius))

    def moves_circular(self, frames_via, frames_to, velocity, max_radius):
        kwargs_dict = {self._get_var_name("poses_via"):
                       self._frames_to_poses(frames_via),
                       self._get_var_name("poses_to"):
                       self._frames_to_poses(frames_to),
                       self._get_var_name("radii"):
                       self._radii_between_frames(frames_to, max_radius),
                       'velocity': velocity}
        func = "movec({1}[i], {2}[i], v={0}, r={3}[i])".format(
                                                       kwargs_dict["velocity"],
                                                       kwargs_dict.keys()[0],
                                                       kwargs_dict.keys()[1],
                                                       kwargs_dict.keys()[2])
        return self._while_move_wrapper(func, **kwargs_dict)

    # IO control
    def add_digital_out(self, number, value):
        """Assign a boolean value to a digital output.

        Parameters
        ----------
        number : integer
            Digital output number.

        value : boolean

        """
        return self.add_line("set_digital_out({}, {})".format(number, value))

    # Utilities
    def _frame_to_pose(self, frame):
        pose = frame.point.data + frame.axis_angle_vector.data
        return "p[{}, {}, {}, {}, {}, {}]".format(*pose)

    def _frames_to_poses(self, frames):
        poses_list = [self._frame_to_pose(frame) for frame in frames]
        return poses_list

    def _radius_between_frames(self, from_frame, via_frame,
                               to_frame, max_radius, div=2.01):
        in_line = Line(from_frame.point, via_frame.point)
        out_line = Line(via_frame.point, to_frame.point)
        return min(max_radius, in_line.length/div, out_line.length/div)

    def _radii_between_frames(self, frames, max_radius):
        radii = []
        for i, frame in enumerate(frames):
            from_frame = frames[max(0, i-1)]
            to_frame = frames[min(i+1, len(frames)-1)]
            if type(max_radius) == list:
                radius = max_radius[i]
            else:
                radius = max_radius
            r = self._radius_between_frames(from_frame, frame, to_frame,
                                            radius)
            radii.append(r)
        return radii

    def _while_move_wrapper(self, func, **kwargs):
        lines = []
        for key, value in kwargs.items():
            print(type(value))
            if isinstance(value, list):
                lines.append('{} = {}'.format(key, value))
        lines.extend(['i = 0',
                      'while i < {}:'.format(min(map(len, filter(islist,
                                             kwargs.values())))),
                      '\t'+func,
                      '\ti = i + 1',
                      'end'])
        print(lines)
        return self.add_lines(lines)

    def _get_var_name(self, var_name, ind=0):
        if var_name in self.var_names:
            new_var_name = var_name + str(ind)
            if new_var_name in self.var_names:
                return self._get_var_name(var_name, ind+1)
            else:
                self.var_names.append(new_var_name)
                return new_var_name
        else:
            self.var_names.append(var_name)
            return var_name

if __name__ == "__main__":
    urscript = URScript()