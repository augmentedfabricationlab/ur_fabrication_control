import os
import socket
from compas.geometry import Line
from ur_fabrication_control.direct_control.communication import URSocketComm

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
        self.header = {}
        self.globals = {}
        self.commands = {}
        self.footer = {}
        self.dictionaries = {
            "header": self.header,      # format {line_nr: URSCRIPT code}
            "globals": self.globals,    # format {variable_name: URSCRIPT code}
            "commands": self.commands,  # format {line_nr: URSCRIPT code}
            "footer": self.footer       # format {line_nr: URSCRIPT code}
        }
        self.ur_ip = ur_ip
        self.ur_port = ur_port
        self.script = None
        self.sockets = {}

        # Functionality
    def start(self, name="program", dictionary="header"):
        """Build the start of the script.

        Parameters
        ----------
        None

        Returns
        -------
        None
            The start line is added to the command dictionary.

        """
        lines = ["def {}():".format(name), "\ttextmsg(\">> Entering {}.\")".format(name)]
        return self.add_lines(lines, to_dict=dictionary, indent=0)

    def end(self, name="program", dictionary="footer"):
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
            for socket_name, data in self.sockets.items():
                if data.get("is_open"):
                    ip, port = [data.get(i) for i in ["ip", "port"]]
                    print("Socket: {} at {}:{} was not closed".format(socket_name, ip, port))
                    self.socket_close(socket_name)
                    print("Socket has been closed at program end")
        lines = ["\ttextmsg(\"<< Exiting {}.\")".format(name), "end"]
        if dictionary == "footer":
            lines.append("{}()\n\n\n".format(name))
        self.add_lines(lines, to_dict=dictionary, indent=0)

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
        script_header = '\n'.join(self.header.values())
        script_globals = '\n'.join(self.globals.values())
        script_commands = '\n'.join(self.commands.values())
        script_footer = '\n'.join(self.footer.values())
        self.script = '\n'.join([script_header, script_globals,
                                 script_commands, script_footer])
        return self.script

    # Dictionary building
    def add_line(self, line, to_dict="commands", key=None, indent=1):
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
        _dict = self.dictionaries.get(to_dict)
        if key is None:
            if len(_dict)!=0:
                key = max(_dict.keys())+1
            else:
                key = 0
        if key in _dict:
            value = _dict.get(key)
            print("Replaced {} with {}".format(value, line))
        _dict[key] = "\t"*indent+line
        return line

    def add_lines(self, lines, to_dict="commands", keys=None, indent=1):
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
        _dict = self.dictionaries.get(to_dict)
        if keys is None:
            if len(_dict)!=0:
                start_key = max(_dict.keys())+1
            else:
                start_key = 0
            alt_keys = list(range(start_key, start_key+len(lines)))
        keys = alt_keys if keys is None else keys
        for (key, line) in zip(keys, lines):
            self.add_line(line, to_dict, key, indent)
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
        pose_type = {
            "cartesian": "get_forward_kin()",
            "joints": "get_actual_joint_positions()"
        }
        func = pose_type.get(get_type)
        self.add_lines(["current_pose = {}".format(func), "textmsg(current_pose)"])
        if send:
            self.socket_send_line('current_pose', socket_name, address)
        return func

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
            print("UR at {} not available on port {}".format(self.ur_ip, self.ur_port))
            raise ConnectionError
        finally:
            enc_script = self.script.encode('utf-8')
            # encoding allows use of python 3.7
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
        # tcp = [tcp[i]/1000 if i < 3 else tcp[i] for i in range(len(tcp))]
        tcp = [tcp[i] for i in range(len(tcp))]
        return self.add_line("set_tcp(p{})".format(tcp))

    def set_payload(self, payload, CoG=None):
        """Set the mass of the tool and elements attached to the tool.

        Parameters
        ----------
        payload : float
            Mass of the payload in kg.
            1.140
        CoG : list of floats
            Center of mass.
            List of three positions [ Cx, Cy, Cz ] in meters (m).

        Returns
        -------
        None
        """
        if CoG is not None:
            self.add_line("set_payload({}, {})".format(str(payload), str(CoG)))
        else:
            self.add_line("set_payload({})".format(str(payload)))

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
        return self.add_line("movel({}, v={}, r={})".format(pose, velocity, radius))

    def move_joint(self, joint_configuration, velocity, radius=0.0):
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
        joint_values = joint_configuration.joint_values
        return self.add_line("movej({}, v={}, r={})".format(joint_values, velocity, radius))

    def move_process(self, configuration=None, frame=None, velocity=0.05, radius=0.0):
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
        if configuration is None:
            pose = self._frame_to_pose(frame)
        elif frame is None:
            pose = configuration.joint_values
        return self.add_line("movep({}, v={}, r={})".format(pose,velocity,radius))

    def move_tool_by_distance(self, x_distance=0.0, y_distance=0.0, z_distance=0.0, velocity=0.01, radius=0, indent=1):
        self.add_line("current_pose = get_actual_tcp_pose()", indent=indent)
        self.add_line("target_pose = pose_trans(current_pose, p[{}, {}, {}, 0, 0, 0])".format(x_distance, y_distance, z_distance), indent=indent)
        return self.add_line("movel(target_pose, v={}, r={})".format(velocity, radius), indent=indent)


    def rotate_joint_by_angle(self, joint_index=0, angle=0.0, velocity=0.1, radius=0.0):
        """Rotate a joint by angle.

        Parameters
        ----------
        joint_index : integer
            An index for which joint to rotate.
            0: base, 1: shoulder, 2: elbow, 3: wrist1, 4: wrist2, 5: wrist3
            
        angle : float
            Angle to rotate in radians.

        Returns
        -------
        None
            A rotation command is added to the command dictionary.
        """
        if joint_index not in range(6):
            raise ValueError("Joint index must be an integer in the range 0 to 5.")
        
        self.add_line("joint_values = get_actual_joint_positions()")
        self.add_line("joint_values[{}] = joint_values[{}] + {}".format(joint_index, joint_index, angle))
        return self.add_line("movej(joint_values, v={}, r={})".format(velocity, radius))

    def get_force(self):
        """Get the tcp force value.
        """
        func = "force()"
        self.add_lines(["force_value = {}".format(func), "textmsg(force_value)"])
        return func

    def force_mode(self, selection_vector, force_limits, speed_limits, indent=1):
        """Get the robot in the force mode.

        Parameters
        ----------
        selection vector : sequence of 0s and 1s.
            List of the compliant axes of x, y, z, dx, dy, dz.
            [0, 0, 1, 0, 0, 0]
        force limits : sequence of floats
            Force limits in N (Newton) for the compliant axes.
            [0.0, 0.0, 10.0, 0.0, 0.0, 0.0]
        speed limits : sequence of floats
            Speed limits in m/s for the compliant axes.
            [0.01, 0.01, 0.025, 0.01, 0.01, 0.01]

        Returns
        -------
        None
            Robot is in the force mode.
        """
        self.add_line("force_mode(tool_pose(), {}, {}, 2, {})".format(str(selection_vector), str(force_limits), str(speed_limits)), indent=indent)

    def move_force_mode(self, force_x=0.0, speed_x=0.01, force_y=0.0, speed_y=0.01, force_z=0.0, speed_z=0.01, indent=1):
        """Get the robot in the force mode.

        Parameters
        ----------
        max force : float
            Force limit in N (Newton) for the z axis.
            10.0
        max speed : float
            Speed limit in m/s for the z axis.
            0.025

        Returns
        -------
        None
            Robot is in the force mode in defined axes.
        """
        if force_x != 0.0:
            x = 1
        else:
            x = 0
        if force_y != 0.0:
            y = 1
        else:
            y = 0
        if force_z != 0.0:
            z = 1
        else:
            z = 0
        self.force_mode([x, y, z, 0, 0, 0], [force_x, force_y, force_z, 0.0, 0.0, 0.0], [speed_x, speed_y, speed_z, 0.01, 0.01, 0.01], indent=indent)

    def rotate_force_mode(self, axis="x", force=0.0, speed=0.01, indent=1):
        """Get the robot in the force mode only in z axis.

        Parameters
        ----------
        axis : str
            Axis the rotation is around.
        max force : float
            Force limit in N (Newton) for the z axis.
            10.0
        max speed : float
            Speed limit in m/s for the z axis.
            0.025

        Returns
        -------
        None
            Robot is in the force mode around defined axis.
        """

        if axis == "x":
            self.force_mode([0, 0, 0, 1, 0, 0], [0.0, 0.0, 0.0, force, 0.0, 0.0], [0.01, 0.01, 0.01, speed, 0.01, 0.01], indent=indent)
        if axis == "y":
            self.force_mode([0, 0, 0, 0, 1, 0], [0.0, 0.0, 0.0, 0.0, force, 0.0], [0.01, 0.01, 0.01, 0.01, speed, 0.01], indent=indent)
        if axis == "z":
            self.force_mode([0, 0, 0, 0, 0, 1], [0.0, 0.0, 0.0, 0.0, 0.0, force], [0.01, 0.01, 0.01, 0.01, 0.01, speed], indent=indent)

    def end_force_mode(self, indent=1):
        self.add_line("end_force_mode()", indent=indent)

    def stop_by_force(self, max_force, log_force=False, indent=1):
        """Stop the robot when the max force is reached.

        Parameters
        ----------
        max force : float
            Force limit in N (Newton) for the robot to stop.
            10.0

        Returns
        -------
        None
            Robot stopped when max force is reached.
        """
        self.add_line("while force() < {}:".format(str(max_force)), indent=indent)
        
        if log_force:
            self.add_line("\ttextmsg(force())", indent=indent)
        
        self.add_lines(["\tsleep(0.01)", "end"], indent=indent)
        self.add_line("\tsleep({})".format(1.0), indent=indent)
        self.end_force_mode(indent=indent)

    def stop_by_distance(self, max_distance, timeout=None, log_distance=False, log_force=False, indent=1):
        """Stop the robot when the max force is reached.

        Parameters
        ----------
        max distance : float
            In meters.
            10.0
        timeout : float
            In seconds.

        Returns
        -------
        None
            Robot stopped when max distance is reached.
        """
        self.add_line("\tsleep({})".format(1.0), indent=indent)
        self.add_lines(["start_pose = get_actual_tcp_pose()", "start_time = 0.00"], indent=indent)

        if timeout != None:
            self.add_line("while pose_dist(start_pose, get_actual_tcp_pose()) < {} and start_time < {}:".format(str(max_distance), str(timeout)), indent=indent)
        else:
            self.add_line("while pose_dist(start_pose, get_actual_tcp_pose()) < {}:".format(str(max_distance)), indent=indent)
        
        if log_distance:
            self.add_line("\ttextmsg(pose_dist(start_pose, get_actual_tcp_pose()))", indent=indent)

        if log_force:
            self.add_line("\ttextmsg(force())", indent=indent)

        self.add_lines(["\tstart_time = start_time + 0.01", "\tsleep(0.01)", "end"], indent=indent)
        self.add_line("end_force_mode()", indent=indent)
        self.add_line("\tsleep({})".format(2.0), indent=indent)

    def stop_by_distance_t(self, max_distance):
        """Stop the robot when the max force is reached.

        Parameters
        ----------
        max distance : float
            In meters.
            10.0

        Returns
        -------
        None
            Robot stopped when max distance is reached.
        """
        self.add_line("\tsleep({})".format(1.0))
        self.add_line("start_pose = get_actual_tcp_pose()")
        self.add_lines(["while pose_dist(start_pose, get_actual_tcp_pose()) < {}:".format(str(max_distance)), "\ttextmsg(pose_dist(start_pose, get_actual_tcp_pose()))","\tsleep(0.01)", "end"])
        self.add_line("end_force_mode()")
        self.add_line("\tsleep({})".format(2.0))

    def stop_by_rotation(self, axis="x", max_rotation=0.0, log_rotation=False, log_force=False, indent=1):
        """Stop the robot when the max force is reached.

        Parameters
        ----------
        axis : str
            Axis the rotation is around.
        max rotation : float
            Rotation limit in radians.

        Returns
        -------
        None
            Robot stopped when max rotation is reached.
        """
        axis_index = {"x": 3, "y": 4, "z": 5}.get(axis)

        self.add_line("\tsleep({})".format(1.0), indent=indent)
        self.add_line("start_pose = get_actual_tcp_pose()", indent=indent)
        self.add_line("while norm(pose_sub(start_pose, get_actual_tcp_pose())[{}]) < {}:".format(str(axis_index), str(max_rotation)), indent=indent)

        if log_rotation:
            self.add_line("\ttextmsg(pose_sub(start_pose, get_actual_tcp_pose()))", indent=indent)

        if log_force:
            self.add_line("\ttextmsg(force())", indent=indent)
        
        self.add_lines(["\tsleep(0.01)", "end"], indent=indent)
        self.add_line("end_force_mode()", indent=indent)
        self.add_line("\tsleep({})".format(2.0), indent=indent)


    def add_digital_out(self, number, value):
        """Assign a boolean value to a digital output.

        Parameters
        ----------
        number : integer
            Digital output number.

        value : boolean

        """
        return self.add_line("set_digital_out({}, {})".format(number,value))

    # Setting variables
    def set_variable(self, variable_name, value):
        self.add_line("{} = {}".format(variable_name,value), dict="globals", key=variable_name)

    def textmessage(self, message, string=False):
        if string:
            self.add_line('textmsg("{}")'.format(message))
        else:
            self.add_line('textmsg({})'.format(message))

    # Utilities
    def _frame_to_pose(self, frame):
        pose = frame.point.__data__ + frame.axis_angle_vector.__data__
        return "p[{}, {}, {}, {}, {}, {}]".format(*pose)

    def _frames_to_poses(self, frames):
        return NotImplementedError
        poses_list = [self._frame_to_pose(frame) for frame in frames]
        poses_list = ', '.join(poses_list)
        return '[' + poses_list + ']'

    def _radius_between_frames(self, from_frame, via_frame,
                               to_frame, max_radius, div=2.01):
        in_line = Line(from_frame.point, via_frame.point)
        out_line = Line(via_frame.point, to_frame.point)
        return min(max_radius, in_line.length/div, out_line.length/div)


if __name__ == "__main__":
    from compas.geometry import Frame

    server_port = 50005
    server_ip = "192.168.56.105"
    ur_ip = "192.168.56.102"
    ur_port = 30002
    # must be changed to meters for testing!
    tcp = [0.0, 0, 0.1, 0.0, 0.0, 0.0]
    urscript = URScript(ur_ip="192.168.0.210", ur_port=30002)
    frames = [Frame.worldXY() for i in range(5)]
    print(urscript._frames_to_poses(frames))
    urscript.start()
    urscript.set_tcp(tcp)
    urscript.set_socket(server_ip, server_port, "Feedbackserver")
    urscript.socket_open("Feedbackserver")
    # urscript.get_force()
    # urscript.force_mode_in_z(10.0, 0.025)
    # urscript.stop_by_force(10.0)
    urscript.get_current_pose_cartesian(socket_name="Feedbackserver", send=True)
    urscript.move_linear(frames[0])
    urscript.get_current_pose_cartesian(socket_name="Feedbackserver", send=True)
    urscript.socket_close(name="Feedbackserver")
    urscript.end()
    urscript.generate()
    print(urscript.script)
    urscript.send_script()
