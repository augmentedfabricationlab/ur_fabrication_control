from __future__ import absolute_import

import os
from ur_fabrication_control.utilities import read_file_to_string


class AirpickMixins:
    def airpick_on(self, adv_mode=True, max_vac=75, min_vac=25, timeout=10, detect=True, grip_sock=1):
        """Turn airpick on"""
        settings = [
            "advanced_mode={}".format(adv_mode),
            "maximum_vacuum={}".format(max_vac),
            "minimum_vacuum={}".format(min_vac),
            "timeout_ms={}".format(timeout),
            "wait_for_object_detected={}".format(detect),
            'gripper_socket="{}"'.format(grip_sock)
        ]
        str_settings = ', '.join(settings)
        self.add_line('\trq_vacuum_grip({})'.format(str_settings))

    def airpick_off(self, adv_mode=True, off_dist=1, detect=True, grip_sock=1, pressure=255, timeout=255, sleep=0.1):
        """Turn airpick off"""
        settings = [
            "advanced_mode={}".format(adv_mode),
            "shutoff_distance_cm={}".format(off_dist),
            "wait_for_object_released={}".format(detect),
            'gripper_socket="{}"'.format(grip_sock),
            "pressure={}".format(pressure),
            "timeout={}".format(timeout),
        ]
        str_settings = ', '.join(settings)
        self.add_line('\trq_vacuum_release({})'.format(str_settings))
        self.add_line("\tsleep({})".format(sleep))

    def add_airpick_commands(self):
        """Add airpick functionality to the script"""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
        program_file = os.path.join(path, "airpick_methods.script")
        program_str = read_file_to_string(program_file)
        self.add_line(program_str, 2)
