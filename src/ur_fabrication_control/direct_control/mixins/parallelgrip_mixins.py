from __future__ import absolute_import

import os


class ParallelGripMixins:
    def grip_open(self, sleep=1.0):
        """Open the parallel gripper.
        """
        self.add_digital_out(6, True) # Digital output 6 is connected to Valve output 4, connected to the right side on the gripper.
        self.add_digital_out(7, False) # Digital output 7 is connected to Valve output 2, connected to the left side on the gripper.
        self.add_line("\tsleep({})".format(sleep))

    def grip_close(self, sleep=1.0):
        """Close the parallel gripper.
        """
        self.add_digital_out(6, False) # Digital output 6 is connected to Valve output 4, connected to the right side on the gripper.
        self.add_digital_out(7, True) # Digital output 7 is connected to Valve output 2, connected to the left side on the gripper.
        self.add_line("\tsleep({})".format(sleep))
