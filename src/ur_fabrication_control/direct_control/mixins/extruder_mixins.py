from __future__ import absolute_import
from ur_fabrication_control.direct_control.urscript import URScript

import os

class ExtruderMixins:
    def extruder_on(self, sleep=1.0, indent=1):
        """Turn on the extruder.
        """
        self.add_digital_out(3, True, indent=indent)
        self.add_line("\tsleep({})".format(sleep), indent=indent)

    def extruder_off(self, sleep=1.0, indent=1):
        """Turn off the extruder.
        """
        self.add_digital_out(3, False, indent=indent)
        self.add_line("\tsleep({})".format(sleep), indent=indent)

class URScript_Extruder(URScript, ExtruderMixins):
    pass