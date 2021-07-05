from __future__ import absolute_import
import os
import socket
from compas.geometry import Line
# from .mixins.airpick_mixins import AirpickMixins

__all__ = [
    'URScript'
]


class URScript(object):
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
                        "\t# open line for airpick commands"])

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

    def textmessage(self, message, string=False):
        if string:
            self.add_line['\ttextmsg("{}")'.format(message)]
        else:
            self.add_line['\ttextmsg({})'.format(message)]

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

    def socket_open(self, ip="192.168.10.11", port=50002, name="socket_0"):
        """Open socket connection
        """
        self.add_lines(['\ttextmsg("Opening socket connection...")',
                       '\tsocket_open("{}", {}, "{}")'.format(ip, port, name)])
        self.sockets[name] = (ip, port)

    def socket_close(self, name="socket_0"):
        """Close socket connection
        """
        self.add_lines(['\ttextmsg("Closing socket connection' +
                        ' with {}...")'.format(name),
                        '\tsocket_close(socket_name=' +
                        '"{}")'.format(self.__get_socket_name(name))])
        del self.sockets[name]

    def __get_socket_name(self, name, address=None):
        if name in self.sockets.keys():
            return name
        elif (address != ("192.168.10.11", 50002)
              and (address in self.sockets.values())):
            return self.sockets.keys()[self.sockets.values().index(address)]
        else:
            raise Exception("No open sockets available with name or address!")

    def socket_send_line_string(self, line, socket_name="socket_0",
                                address=("192.168.10.11", 50002)):
        """Send a single line to the socket.

        Parameters
        ----------
        line : string
            A single line to send to the socket.

        Returns
        -------
        None

        """
        sock_name = self.__get_socket_name(socket_name, address)
        str_line = '\tsocket_send_line("{}", socket_name="{}")'
        self.add_line(str_line.format(line, sock_name))

    def socket_send_line(self, line, socket_name="socket_0",
                         address=("192.168.10.11", 50002)):
        """Send a single line to the socket.

        Parameters
        ----------
        line : string
            A single line to send to the socket.

        Returns
        -------
        None

        """
        sock_name = self.__get_socket_name(socket_name, address)
        str_line = '\tsocket_send_line({}, socket_name="{}")'
        self.add_line(str_line.format(line, sock_name))

    def socket_send_ints(self, integers, var_name="ints",
                         socket_name="socket_0",
                         address=("192.168.10.11", 50002)):
        sock_name = self.__get_socket_name(socket_name, address)
        v_name = self._get_var_name(var_name)
        self.add_lines([
            '\t{} = {}'.format(v_name, integers),
            '\ti = 0',
            '\twhile i < {}:'.format(len(integers)),
            '\t\tsent = socket_send_int({}[i], '.format(v_name) +
            'socket_name="{}")'.format(sock_name),
            '\t\tif sent == True:',
            '\t\t\ttextmsg("msg sent: ", {}[i])'.format(v_name),
            '\t\t\ti = i + 1',
            '\t\t\tsent = False',
            '\t\tend',
            '\tend'
        ])

    def socket_send_int(self, integer, socket_name="socket_0",
                        address=("192.168.10.11", 50002)):
        sock_name = self.__get_socket_name(socket_name, address)
        self.add_lines([
            '\tsent = False',
            '\twhile sent == False:',
            '\t\tsent = socket_send_int' +
            '({}, socket_name="{}")'.format(integer, sock_name),
            '\tend'
        ])

    def socket_send_float(self, float_value, socket_name="socket_0",
                          address=("192.168.10.11", 50002)):
        raise NotImplementedError

    def socket_send_bytes(self, bytes_list, socket_name="socket_0",
                          address=("192.168.10.11", 50002)):
        sock_name = self.__get_socket_name(socket_name, address)
        self.add_lines([
            '\tfloat_bytes = {}'.format(bytes_list),
            '\ti = 0',
            '\twhile i < {}:'.format(len(bytes_list)),
            '\t\tsent = socket_send_byte(float_bytes[i], ' +
            'socket_name="{}")'.format(sock_name),
            '\t\tif sent == True:',
            '\t\t\ttextmsg("msg (byte) sent: ", float_bytes[i])',
            '\t\t\ti = i + 1',
            '\t\t\tsent = False',
            '\t\tend',
            '\tend'
        ])

    def socket_send_byte(self, byte, socket_name="socket_0",
                         address=("192.168.10.11", 50002)):
        """Send a single line to the socket.

        Parameters
        ----------
        byte : bytes
            Byte to send to the socket.

        Returns
        -------
        None

        """
        sock_name = self.__get_socket_name(socket_name, address)
        self.add_lines([
            '\tsent = False',
            '\twhile sent == False:',
            '\t\tsent = socket_send_byte' +
            '({}, socket_name="{}")'.format(byte, sock_name),
            '\tend'
        ])

    def socket_read_binary_integer(self, var_name="msg_recv_0", number=1,
                                   socket_name="socket_0",
                                   address=("192.168.10.11", 50002),
                                   timeout=2):
        sock_name = self.__get_socket_name(socket_name, address)
        self.add_lines([
            '\t{} = '.format(var_name) +
            'socket_read_binary_integer({}, '.format(number) +
            'socket_name={}, timeout={})'.format(sock_name, timeout),
            '\ttextmsg({})'.format(var_name)
        ])

    def socket_read_string(self, var_name="msg_recv_0", prefix="", suffix="",
                           int_escape=False, socket_name="socket_0",
                           address=("192.168.10.11", 50002), timeout=2):
        sock_name = self.__get_socket_name(socket_name, address)
        self.add_lines([
            '\t{} = socket_read_string'.format(var_name) +
            '(socket_name="{}", prefix="{}", '.format(sock_name, prefix) +
            'suffix="{}", interpret_escape={}'.format(suffix, int_escape) +
            ', timeout={})'.format(timeout),
            '\ttextmsg({})'.format(var_name)
        ])

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
        [self.add_line(line, i+ind) for (ind, line) in enumerate(lines)]

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
        pose_type = {
            "cartesian": "get_forward_kin()",
            "joints": "get_actual_joint_positions()"
        }
        self.add_lines(["\tcurrent_pose = {}".format(pose_type[get_type]),
                        "\ttextmsg(current_pose)"])
        if send:
            self.socket_send_line('current_pose\n', socket_name, address)

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
        self.add_line("\tset_tcp(p{})".format(tcp))

    def _radius_between_frames(self, from_frame, via_frame,
                               to_frame, max_radius):
        in_line = Line(from_frame.point, via_frame.point)
        out_line = Line(via_frame.point, to_frame.point)
        r = min(max_radius, in_line.length/2, out_line.length/2)
        return r

    def moves_linear(self, frames, velocity=0.05, max_radius=0.1):
        # Multiple moves, can calculate the radius
        for i, frame in enumerate(frames):
            from_frame = frames[max(0, i-1)]
            to_frame = frames[min(i+1, len(frames)-1)]
            r = self._radius_between_frames(from_frame, frame, to_frame,
                                            max_radius)
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
        line = "\tmovel(p{}, v={}, r={})".format(pose, velocity, radius)
        self.add_line(line)

    def moves_joint(self, joint_configurations, velocity):
        # multiple joint positions
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
        line = "\tmovej({}, v={})"
        self.add_line(line.format(joint_configuration.values(), velocity))

    def moves_process(self, frames, velocity=0.05, max_radius=0):
        # multiple moves, can calculate the radius
        for i, frame in enumerate(frames):
            from_frame = frames[max(0, i-1)]
            to_frame = frames[min(i+1, len(frames)-1)]
            r = self._radius_between_frames(from_frame, frame, to_frame,
                                            max_radius)
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
        line = "\tmovep(p{}, v={}, r={})".format(pose, velocity, radius)
        self.add_line(line)

    def moves_circular(self, frames_via, frames_to, velocity, max_radius):
        for i, (frame_via, frame_to) in enumerate(zip(frames_via, frames_to)):
            r = self._radius_between_frames(frames_to[max(0, i-1)], frame_via,
                                            frame_to, max_radius)
            self.move_circular(frame_via, frame_to, velocity, r)

    def move_circular(self, frame_via, frame_to, velocity, radius):
        """
        """
        pose_via = frame_via.point.data + frame_via.axis_angle_vector.data
        pose_to = frame_to.point.data + frame_to.axis_angle_vector.data
        line = "\tmovec(p{}, p{}, v={}, r={})"
        self.add_line(line.format(pose_via, pose_to, velocity, radius))

    def digital_out(self, number, value):
        """
        """
        self.add_line("\tset_digital_out({}, {})".format(number, value))

    def areagrip_on(self, sleep=1.0):
        """
        """
        self.add_digital_out(7, True)
        self.add_line("\tsleep({})".format(sleep))

    def areagrip_off(self, sleep=0.1):
        """
        """
        self.add_digital_out(7, False)
        self.add_line("\tsleep({})".format(sleep))
