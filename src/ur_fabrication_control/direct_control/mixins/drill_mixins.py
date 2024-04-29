from __future__ import absolute_import
from ur_fabrication_control.direct_control.urscript import URScript

import os

class DrillMixins:
    def drill_on(self, sleep=1.0):
        """Turn on the drill.
        """
        self.add_digital_out(3, True)
        self.add_line("\tsleep({})".format(sleep))

    def drill_off(self, sleep=1.0):
        """Turn off the drill.
        """
        self.add_digital_out(3, False)
        self.add_line("\tsleep({})".format(sleep))

class URScript_Drill(URScript, DrillMixins):
    pass