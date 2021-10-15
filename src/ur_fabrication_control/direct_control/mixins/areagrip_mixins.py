from __future__ import absolute_import

import os


class AreaGripMixins:
    def areagrip_on(self, sleep=1.0):
        """Turn the area gripper on.
        """
        self.add_digital_out(6, True) # Digital output 6 is connected to Valve output 4, connected to the supply on the gripper.
        self.add_digital_out(7, False) # Digital output 7 is connected to Valve output 2, connected to the blow-off on the gripper. (next to silencer)
        self.add_line("\tsleep({})".format(sleep))

    def areagrip_blowoff(self, sleep=1.0):
        """Let the area gripper blow off.
        """
        self.add_digital_out(7, True)
        self.add_digital_out(6, True) # Digital output 6 is connected to Valve output 4, connected to the supply on the gripper.
        self.add_digital_out(7, True) # Digital output 7 is connected to Valve output 2, connected to the blow-off on the gripper. (next to silencer)
        self.add_line("\tsleep({})".format(sleep))

    def areagrip_off(self, sleep=0.1):
        """Turn the area gripper off.
        """
        self.add_digital_out(6, False) # Digital output 6 is connected to Valve output 4, connected to the supply on the gripper.
        self.add_digital_out(7, False) # Digital output 7 is connected to Valve output 2, connected to the blow-off on the gripper. (next to silencer)
        self.add_line("\tsleep({})".format(sleep))
