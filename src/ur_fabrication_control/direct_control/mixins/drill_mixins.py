from __future__ import absolute_import
from ur_fabrication_control.direct_control.urscript import URScript

import os

class DrillMixins:
    def drill_on(self, sleep=1.0, indent=1):
        """Turn on the drill.
        """
        self.add_digital_out(3, True, indent=indent)
        self.add_line("\tsleep({})".format(sleep), indent=indent)

    def drill_off(self, sleep=1.0, indent=1):
        """Turn off the drill.
        """
        self.add_digital_out(3, False, indent=indent)
        self.add_line("\tsleep({})".format(sleep), indent=indent)

class URScript_Drill(URScript, DrillMixins):
    pass