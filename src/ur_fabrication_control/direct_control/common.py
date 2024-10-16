import os
import sys
import socket
import time
from ur_fabrication_control.direct_control.urscript import URScript
from ur_fabrication_control.direct_control.communication import TCPFeedbackServer
from threading import Thread
if sys.version_info[0] == 3:
    from queue import Queue
else:
    from Queue import Queue

__all__ = [
    'is_available',
    'send_script',
    'send_stop',
    'generate_moves_linear',
    'generate_script_pick_and_place_block',
    'generate_airpick_toggle',
    'generate_areagrip_toggle',
    'get_current_pose_cartesian',
    'get_current_pose_joints'
]



def is_available(ip):
    """Ping the UR network to check for availability.

    Parameters
    ----------
    ip : string
        IP of the UR Robot.

    Returns
    -------
    boolean
        "True" if available.
        "False" if unavailable.

    """
    system_call = "ping -r 1 -n 1 {}".format(ip)
    response = os.system(system_call)
    if response == 0:
        return True
    else:
        return False


def send_script(script, ip, port=30002):
    """Send a script to the UR Robot.

    Parameters
    ----------
    script : string
        A script to send to robot.

    ip : string
        IP of the UR Robot.

    port : integer
        Port number of the UR Robot.
        Default set to "30002".

    Returns
    -------
    None

    """
    try:
        s = socket.create_connection((ip, port), timeout=2)
    except socket.timeout:
        print("UR with ip {} not available on port {}".format(ip, port))
    finally:
        enc_script = script.encode('utf-8')  # encoding allows use of python 3.7
        s.send(enc_script)
        print("Script sent to {} on port {}".format(ip, port))
        s.close()


def send_stop(ip, port):
    """Send stop script to the UR Robot.

    Parameters
    ----------
    ip : string
        IP of the UR Robot.

    port : integer
        Port number of the UR Robot.

    Returns
    -------
    None

    """
    ur_cmds = URScript(ur_ip=ip, ur_port=port)
    ur_cmds.start()
    ur_cmds.add_line("\tstopl(0.5)")
    ur_cmds.end()
    ur_cmds.generate()
    ur_cmds.send_script()


def generate_moves_linear(tcp, frames, ur_ip, ur_port, velocity=0.05, radius=0):
    """Generate linear movement.

    Parameters
    ----------
    tcp : sequence of float
        Tool center point in a form of list.
        tcp = [x, y, z, dx, dy, dz]

    move_commands : sequence of sequence of floats
        List of move_command, which is a list of x, y, z position, dx, dy, dz axis, velocity and radius.
        move_commands = [move_command_1, move_command_2, ...]
        move_command = [x, y, z, dx, dy, dz, v, r]

    ur_ip : string
        IP of the UR Robot.

    ur_port : integer
        Port number of the UR Robot.

    server_ip : string (None)
        IP of the server.

    server_port : integer (None)
        Port number of the server.

    Returns
    -------
    object
        URScript

    """
    ur_cmds = URScript(ur_ip=ur_ip, ur_port=ur_port)
    ur_cmds.start()
    ur_cmds.set_tcp(tcp)
    if type(frames) == list:
        ur_cmds.moves_linear(frames, velocity, radius)
    else:
        ur_cmds.move_linear(frames, velocity, radius)
    ur_cmds.end()
    ur_cmds.generate()
    return ur_cmds


def generate_script_pick_and_place_block(tcp, frames, ur_ip, ur_port, velocity = 0.05, radius = 0, vacuum_on=2, vacuum_off=5):
    """Generate multiple linear movements and Airpick on/off commands.

    Parameters
    ----------
    tcp : sequence of float
        Tool center point in a form of list.
        tcp = [x, y, z, dx, dy, dz]

    move_commands : sequence of sequence of floats
        List of move_command, which is a list of x, y, z position, dx, dy, dz axis, velocity and radius.
        move_commands = [move_command_1, move_command_2, ...]
        move_command = [x, y, z, dx, dy, dz, v, r]

    ur_ip : string
        IP of the UR Robot.

    ur_port : integer
        Port number of the UR Robot.

    server_ip : string (None)
        IP of the server.

    server_port : integer (None)
        Port number of the server.

    vacuum_on : integer
        Default set to 2.

    vacuum_off : integer
        Default set to 5.

    Returns
    -------
    object
        URScript

    """
    ur_cmds = URScript(ur_ip=ur_ip, ur_port=ur_port)
    ur_cmds.start()
    ur_cmds.add_airpick_commands()
    ur_cmds.set_tcp(tcp)
    for i, frame in enumerate(frames):
        if i == vacuum_on:
            ur_cmds.airpick_on()
        elif i == vacuum_off:
            ur_cmds.airpick_off()
        else:
            pass
        ur_cmds.move_linear(frame, velocity, radius)
    ur_cmds.end()
    ur_cmds.generate()
    return ur_cmds


def generate_airpick_toggle(toggle, ur_ip, ur_port, max_vac=75, min_vac=25, detect=True, pressure=55, timeout=55):
    """Toggle the Airpick on/off.

    Parameters
    ----------
    toggle : boolean
        Set to "True" for Airpick on.
        Set to "False" for Airpick off.

    ur_ip : string
        IP of the UR Robot.

    ur_port : integer
        Port number of the UR Robot.

    max_vac : integer
        Maximum vacuum for Airpick on.
        Default set to 75.

    min_vac : integer
        Minimum vacuum for Airpick off.
        Default set to 25.

    detect : boolean
        Set to "True" to wait for object detected.
        Default set to "True".

    pressure : integer
        Pressure for Airpick off.
        Default set to 55.

    timeout : integer
        Set the timeout.
        Default set to 55.

    Returns
    -------
    object
        URScript

    """
    ur_cmds = URScript(ur_ip=ur_ip, ur_port=ur_port)
    ur_cmds.start()
    ur_cmds.add_airpick_commands()
    if toggle:
        ur_cmds.airpick_on(max_vac, min_vac, detect)
    elif not toggle:
        ur_cmds.airpick_off(pressure, timeout)
    ur_cmds.end()
    ur_cmds.generate()
    return ur_cmds


def generate_areagrip_toggle(toggle, ur_ip, ur_port, sleep):
    """Toggle the Area Grip on/off.

    Parameters
    ----------
    toggle : boolean
        Set to "True" for Area Grip on.
        Set to "False" for Area Grip off.

    ur_ip : string
        IP of the UR Robot.

    ur_port : integer
        Port number of the UR Robot.

    sleep : float

    Returns
    -------
    object
        URScript

    """

    ur_cmds = URScript(ur_ip=ur_ip, ur_port=ur_port)
    ur_cmds.start()
    if toggle:
        ur_cmds.areagrip_on(sleep=sleep)
    elif not toggle:
        ur_cmds.areagrip_off(sleep=sleep)
    ur_cmds.end()
    ur_cmds.generate()
    return ur_cmds


def get_current_pose_cartesian(tcp, server_ip, server_port, ur_ip, ur_port, send=False):
    """Get the current cartesian coordinates of the UR Robot.

    Parameters
    ----------
    tcp : sequence of float
        Tool center point in a form of list.
        tcp = [x, y, z, dx, dy, dz]

    server_ip : string
        IP of the server.

    server_port : integer
        Port number of the server.

    ur_ip : string
        IP of the UR Robot.

    ur_port : integer
        Port number of the UR Robot.

    send: boolean
        Set to "True" to also send the current pose from the UR Robot to the server.
        Default set to "False" to only print out on the UR Robot's display.

    Returns
    -------
    msg : float

    """
    ur_cmds = URScript(ur_ip=ur_ip, ur_port=ur_port)
    ur_cmds.start()
    ur_cmds.set_tcp(tcp)
    ur_cmds.set_socket(server_ip, server_port, "Feedbackserver")
    ur_cmds.socket_open("Feedbackserver")
    ur_cmds.get_current_pose_cartesian(socket_name="Feedbackserver", send=send)
    ur_cmds.socket_close(name="Feedbackserver")
    ur_cmds.end()
    ur_cmds.generate()
    print(ur_cmds.script)
    with TCPFeedbackServer(ip=server_ip, port=server_port) as server:
        ur_cmds.send_script()
        ms = 0
        while len(server.msgs)==0 and ms<1000:
            time.sleep(0.001)
            ms += 1
    return server.msgs.get(0, "Timed out")

    # return _get_current_pose("cartesian", tcp, server_ip, server_port, ur_ip, ur_port, send)


def get_current_pose_joints(server_ip, server_port, ur_ip, ur_port, send=False):
    """Get the current joint positions of the UR Robot.

    Parameters
    ----------
    server_ip : string
        IP of the server.

    server_port : integer
        Port number of the server.

    ur_ip : string
        IP of the UR Robot.

    ur_port : integer
        Port number of the UR Robot.

    send: boolean
        Set to "True" to also send the current pose from the UR Robot to the server.
        Default set to "False" to only print out on the UR Robot's display.

    Returns
    -------
    msg : float

    """
    ur_cmds = URScript(ur_ip=ur_ip, ur_port=ur_port)
    ur_cmds.start()
    ur_cmds.set_socket(server_ip, server_port, "Feedbackserver")
    ur_cmds.socket_open("Feedbackserver")
    ur_cmds.get_current_pose_joints(send)
    ur_cmds.socket_close(name="Feedbackserver")
    ur_cmds.end()
    ur_cmds.generate()
    with TCPFeedbackServer(ip=server_ip, port=server_port) as server:
        ur_cmds.send_script()
        ms = 0
        while len(server.msgs)==0 and ms<1000:
            time.sleep(0.001)
            ms += 1
    return server.msgs.get(0, "Timed out")

    #return _get_current_pose("joints", tcp, server_ip, server_port, ur_ip, ur_port, send)

"""
def _get_current_pose(pose_type, tcp, server_ip, server_port, ur_ip, ur_port, send):

    ur_cmds = URScript(server_ip=server_ip, server_port=server_port, ur_ip=ur_ip, ur_port=ur_port)
    ur_cmds.start()
    ur_cmds.set_tcp(tcp)
    pose_type_map = {"cartesian": ur_cmds.get_current_pose_cartesian,
                     "joints": ur_cmds.get_current_pose_joints}
    pose_type_map[pose_type](send)
    ur_cmds.end(feedback=True)
    ur_cmds.generate()
    server = TCPFeedbackServer(ip=server_ip, port=server_port)
    server.start()
    ur_cmds.send_script()
    server.listen(timeout=5)
    time.sleep(1)
    server.close()
    server.join()
    return server.msgs[0]
"""

if __name__ == "__main__":
    server_port = 50005
    server_ip = "192.168.0.250"
    ur_ip = "192.168.0.210"
    ur_port = 30002
    # must be changed to meters for testing!
    tcp = [0.0, 0, 0.1, 0.0, 0.0, 0.0]
    msg = get_current_pose_cartesian(tcp, server_ip, server_port, ur_ip, ur_port, send=True)

    print(msg)
    