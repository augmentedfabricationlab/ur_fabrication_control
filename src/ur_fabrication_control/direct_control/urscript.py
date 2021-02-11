from __future__ import absolute_import
import os
import socket
from compas.geometry import Frame, Line
from .mixins.airpick_mixins import AirpickMixins

__all__ = [
    'URScript'
]


class URScript():
    """Class to build a script of commands for the UR Robot system.

    Parameters
    ----------
    server_ip : string (None)
        IP of the server.
    server_port : integer (None)
        Port number of the server.
    ur_ip : string (None)
        IP of the UR Robot.
    ur_port : integer (None)
        Port number of the UR Robot.

    Attributes
    ----------
    commands_dict (read-only) : dictionary
        A dictionary to store the command lines.
    server_ip : string
        IP of the server.
    server_port : integer
        Port number of the server.
    ur_ip : string
        IP of the UR Robot.
    ur_port : integer
        Port number of the UR Robot.
    script (read-only) : string
        A string generated from the commands_dict to be sent to the UR Robot.

    """
    def __init__(self, server_ip=None, server_port=None, ur_ip=None, ur_port=None):
        self.commands_dict = {}
        self.server_ip = server_ip
        self.server_port = server_port
        self.ur_ip = ur_ip
        self.ur_port = ur_port
        self.script = None

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
                        "\t# open line for airpick commands"])

    def end(self, feedback=None):
        """Build the end of the script.

        Parameters
        ----------
        feedback : boolean (None)
            Set to "True" if feedback is desired.

        Returns
        -------
        None
            The end line is added to the command dictionary.

        """
        if feedback:
            self.socket_send_line('"Done"')
        self.add_lines(["\ttextmsg(\"<< Exiting program.\")",
                        "end",
                        "program()\n\n\n"])

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

    def socket_send_line(self, line):
        """Send a single line to the socket.

        Parameters
        ----------
        line : string
            A single line to send to the socket.

        Returns
        -------
        None

        """
        self.add_lines(['\tsocket_open("{}", {})'.format(self.server_ip, self.server_port),
                        '\tsocket_send_line({})'.format(line),
                        "\tsocket_close()"])

    # Dictionary building
    def add_line(self, line, i=None):
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
        self.commands_dict[i] = line

    def add_lines(self, lines):
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
        [self.add_line(line, i+line_nr) for (line_nr, line) in zip(range(len(lines)), lines)]

    # Feedback functionality
    def get_current_pose_cartesian(self, send=False):
        """Get the current cartesian pose.

        Parameters
        ----------
        send : boolean
            Set to "True" to also send the current pose from the UR Robot to the server.
            Default set to "False" to only print out on the UR Robot's display.

        Returns
        -------
        None

        """
        self.get_current_pose("cartesian", send)

    def get_current_pose_joints(self, send=False):
        """Get the current joint positions.

        Parameters
        ----------
        send : boolean
            Set to "True" to also send the current pose from the UR Robot to the server.
            Default set to "False" to only print out on the UR Robot's display.

        Returns
        -------
        None

        """
        self.get_current_pose("joints", send)

    def get_current_pose(self, get_type, send):
        """Create get pose code.

        """
        pose_type = {
            "cartesian": "get_forward_kin()",
            "joints": "get_actual_joint_positions()"
        }
        self.add_lines(["\tcurrent_pose = {}".format(pose_type[get_type]),
                        "\ttextmsg(current_pose)"])
        if send:
            self.socket_send_line('current_pose')
            self.feedback = True
            #self.add_line("\ttextmsg('sending done')")

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

    def send_script_feedback(self):
        """
        """
        #opens server
        self.send_script()
        #closes server

    def send_script(self, feedback=False):
        """Send the generated script to the UR Robot.

        Parameters
        ----------
        feedback : boolean
            Set to "True" if feedback is desired.
            Default set to "False".

        Returns
        -------
        None

        """
        try:
            s = socket.create_connection((self.ur_ip, self.ur_port), timeout=2)
        except socket.timeout:
            print("UR with ip {} not available on port {}".format(self.ur_ip, self.ur_port))
            raise ConnectionError
        finally:
            enc_script = self.script.encode('utf-8') # encoding allows use of python 3.7
            s.send(enc_script)
            print("Script sent to {} on port {}".format(self.ur_ip, self.ur_port))
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
        #tcp = [tcp[i]/1000 if i < 3 else tcp[i] for i in range(len(tcp))]
        tcp = [tcp[i] for i in range(len(tcp))]
        self.add_line("\tset_tcp(p{})".format(tcp))

    def _radius_between_frames(self, from_frame, via_frame, to_frame, max_radius):
        in_line = Line(from_frame.point, via_frame.point)
        out_line = Line(via_frame.point, to_frame.point)
        r = min(max_radius, in_line.length/2, out_line.length/2)
        return r

    def moves_linear(self, frames, velocity=0.05, max_radius=0.1):
        #multiple moves, can calculate the radius
        for i, frame in enumerate(frames):
            r = self._radius_between_frames(frames[max(0,i-1)], frame, frames[min(i+1, len(frames)-1)], max_radius)
            self.move_linear(frame, velocity, r)

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
        pose = frame.point.data + frame.axis_angle_vector.data
        self.add_line("\tmovel(p{}, v={}, r={})".format(pose, velocity, radius))

    def moves_joint(self, joint_configurations, velocity):
        #multiple joint positions
        for joint_configuration in joint_configurations:
            self.move_joint(joint_configuration, velocity)        

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
        self.add_line("\tmovej({}, v={})".format(joint_configuration.values, velocity))

    def moves_process(self, frames, velocity=0.05, max_radius=0):
        #multiple moves, can calculate the radius
        for i, frame in enumerate(frames):
            r = self._radius_between_frames(frames[max(0,i-1)], frame, frames[min(len(frames)+1)], max_radius)
            self.move_process(frame, velocity, r)

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
        pose = frame.point.data + frame.axis_angle_vector.data
        self.add_line("\tmovep(p{}, v={}, r={})".format(pose, velocity, radius))

    def moves_circular(self, frames_via, frames_to, velocity, max_radius):
        for i, (frame_via, frame_to) in enumerate(zip(frames_via, frames_to)):
            r = self._radius_between_frames(frames_to[max(0,i-1)], frame_via, frame_to, max_radius)
            self.move_circular(frame_via, frame_to, velocity, r)

    def move_circular(self, frame_via, frame_to, velocity, radius):
        """
        """
        pose_via = frame_via.point.data + frame_via.axis_angle_vector.data
        pose_to = frame_to.point.data + frame_to.axis_angle_vector.data
        self.add_line("\tmovec(p{}, p{} v={}, r={})".format(pose_via, pose_to, velocity, radius))

    def digital_out(self, number, value):
        """
        """
        self.add_line("\tset_digital_out({}, {})".format(number, value))

    def areagrip_on(self, sleep = 1.):
        """
        """
        self.add_digital_out(7, True)
        self.add_line("\tsleep({})".format(sleep))

    def areagrip_off(self, sleep = 0.1):
        """
        """
        self.add_digital_out(7, False)
        self.add_line("\tsleep({})".format(sleep))

