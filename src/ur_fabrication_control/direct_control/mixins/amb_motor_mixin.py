from __future__ import absolute_import
from ur_fabrication_control.direct_control.urscript import URScript

import os

class AMBMotorMixins:
    def drill_on(self, sleep=1.0, indent=1):
        """Turn on the drill.
        """
        self.add_digital_out(4, True, indent=indent)
        self.add_line("\tsleep({})".format(sleep), indent=indent)

    def speedControl(self, voltage=5.00, indent=1):
        self.add_analog_out(1, voltage, indent=indent)

    def drill_off(self, sleep=1.0, indent=1):
        """Turn off the drill.
        """
        self.add_digital_out(4, False, indent=indent)
        self.add_line("\tsleep({})".format(sleep), indent=indent)

class URScript_AMBMotor(URScript, AMBMotorMixins):
    pass