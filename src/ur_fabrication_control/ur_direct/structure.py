from __future__ import absolute_import
import os
import socket
from ur_fabrication_control.ur_direct.mixins.airpick_mixins import AirpickMixins

__all__ = [
    'URCommandScript'
]


class URCommandScript(AirpickMixins):
    """Class containing commands for the UR Robot system"""
    def __init__(self, server_ip=None, server_port=None, ur_ip=None, ur_port=None):
        self.commands_dict = {}
        self.server_ip = server_ip
        self.server_port = server_port
        self.ur_ip = ur_ip
        self.ur_port = ur_port
        self.script = None

        self.exit_message = "Done"

        # Functionality
    def start(self):
        """To build the start of the script"""
        self.add_lines(["def program():",
                        "\ttextmsg(\">> Entering program.\")",
                        "\t# open line for airpick commands"])

    def end(self, feedback=None):
        """To build the end of the script"""
        if feedback:
            self.socket_send_line('"Done"')
        self.add_lines(["\ttextmsg(\"<< Exiting program.\")",
                        "end",
                        "program()\n\n\n"])

    def generate(self):
        """Translate the dictionary to a long string"""
        self.script = '\n'.join(self.commands_dict.values())
        return self.script

    def socket_send_line(self, line):
        self.add_lines(['\tsocket_open("{}", {})'.format(self.server_ip, self.server_port),
                        '\tsocket_send_line({})'.format(line),
                        "\tsocket_close()"])

    # Dictionary building
    def add_line(self, line, i=None):
        """Add a single line to the script"""
        if i is None:
            i = len(self.commands_dict)
        else:
            pass
        self.commands_dict[i] = line

    def add_lines(self, lines):
        """Add a multiple lines to the script"""
        i = len(self.commands_dict)
        [self.add_line(line, i+line_nr) for (line_nr, line) in zip(range(len(lines)), lines)]

    # Feedback functionality
    def get_current_pose_cartesian(self, send=False):
        """Get the current cartesian pose"""
        self.get_current_pose("cartesian", send)

    def get_current_pose_joints(self, send=False):
        """Get the current joints pose"""
        self.get_current_pose("joints", send)

    def get_current_pose(self, get_type, send):
        """Create get pose code"""
        pose_type = {
            "cartesian": "get_forward_kin()",
            "joints": "get_actual_joint_positions()"
        }
        self.add_lines(["\tcurrent_pose = {}".format(pose_type[get_type]),
                        "\ttextmsg(current_pose)"])
        if send:
            self.socket_send_line('current_pose')
            #self.add_line("\ttextmsg('sending done')")
            
    # Connectivity
    def is_available(self):
        """Ping the network, to check for availability"""
        system_call = "ping -r 1 -n 1 {}".format(self.ur_ip)
        response = os.system(system_call)
        if response == 0:
            return True
        else:
            return False

    def send_script(self):
        try:
            s = socket.create_connection((self.ur_ip, self.ur_port), timeout=2)
        except socket.timeout:
            print("UR with ip {} not available on port {}".format(self.ur_ip, self.ur_port))
            raise
        finally:
            enc_script = self.script.encode('utf-8') # encoding allows use of python 3.7
            s.send(enc_script)
            print("Script sent to {} on port {}".format(self.ur_ip, self.ur_port))
            s.close()

    # Geometric effects
    def set_tcp(self, tcp):
        """Set the tcp"""
        #tcp = [tcp[i]/1000 if i < 3 else tcp[i] for i in range(len(tcp))]
        tcp = [tcp[i] for i in range(len(tcp))]
        self.add_line("\tset_tcp(p{})".format(tcp))

    def add_move_linear(self, move_command, feedback=None):
        """Add a move command to the script"""
        #move = [cmd / 1000 if c not in [3, 4, 5] else cmd for c, cmd in zip(range(len(move_command)), move_command)]
        move = [cmd for c, cmd in zip(range(len(move_command)), move_command)]
        [x, y, z, dx, dy, dz, v, r] = move
        self.add_line("\tmovel(p[{}, {}, {}, {}, {}, {}], v={}, r={})".format(x, y, z, dx, dy, dz, v, r))
        if feedback == "Full":
            self.get_current_pose_cartesian(True)
        elif feedback == "UR_only":
            self.get_current_pose_cartesian(False)
        else:
            pass

    def add_digital_out(self, number, value):
        self.add_line("\tset_digital_out({}, {})".format(number, value))

    def add_areagrip_on(self, sleep = 1.):
        self.add_digital_out(7, True)
        self.add_line("\tsleep({})".format(sleep))

    def add_areagrip_off(self, sleep = 0.1):
        self.add_digital_out(7, False)
        self.add_line("\tsleep({})".format(sleep))

