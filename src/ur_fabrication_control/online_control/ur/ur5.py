from __future__ import print_function

import math

from ur_online_control import get_data

from compas_robots import Configuration
from .ur import UR


class UR5(UR):
    """The UR 5 robot class.

    Manual link:
    #define UR5_PARAMS
    https://github.com/ros-industrial/universal_robot/blob/kinetic-devel/ur_kinematics/src/ur_kin.cpp
    but in mm, not in m
    """

    # define UR5_PARAMS
    d1 = 89.159
    a2 = -425.0
    a3 = -392.25
    d4 = 109.15
    d5 = 94.65
    d6 = 82.3

    shoulder_offset = 135.85
    elbow_offset = -119.7

    # The UR has a very simple workspace definition: it is s sphere with a
    # cylinder in the center cut off. The axis of this cylinder is j0, the
    # diameter is defined below. For more info: UR manual.
    working_area_sphere_diameter = 1850.  # max. working area diameter, recommended 1700
    working_area_cylinder_diameter = 149.

    def __init__(self):
        super(UR5, self).__init__()

    def get_model_path(self):
        print(get_data("robots/ur/ur5"))
        return get_data("robots/ur/ur5")

    def forward_kinematics(self, configuration):
        q = configuration.values[:]
        q[5] += math.pi
        return super(UR5, self).forward_kinematics(Configuration.from_revolute_values(q))

    def inverse_kinematics(self, tool0_frame_RCS):
        configurations = super(UR5, self).inverse_kinematics(tool0_frame_RCS)
        for q in configurations:
            print(q)
        for i in range(len(configurations)):
            configurations[i].values[5] -= math.pi
        return configurations



if __name__ == "__main__":

    import math
    from compas_fab.utilities import sign
    from compas.geometry import Frame
    from .kinematics import format_joint_positions
    ur = UR5()

    q = [-0.44244, -1.5318, 1.34588, -1.38512, -1.05009, -0.4495]
    q = Configuration.from_revolute_values(q)
    Ts = ur.get_forward_transformations(q)
    for T in Ts:
        print(T)
        print()
    frame = ur.forward_kinematics(q)
    qsols = ur.inverse_kinematics(frame)
    for q in qsols:
        print(q)
    ur.get_transformed_model(Ts)
