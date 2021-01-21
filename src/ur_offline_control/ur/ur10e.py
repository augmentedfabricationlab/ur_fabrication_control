from __future__ import absolute_import

import math

from ur_offline_control.ur.configuration import Configuration
from ur_offline_control.ur.ur import UR


class UR10e(UR):
    """The UR 10 robot class.

    Manual link:
    #define UR10_PARAMS
    https://github.com/ros-industrial/universal_robot/blob/kinetic-devel/ur_kinematics/src/ur_kin.cpp
    in meters
    """

    # define UR10_PARAMS
    d1 = 0.1807
    a2 = -0.6127
    a3 = -0.57155
    d4 = 0.17415
    d5 = 0.11985
    d6 = 0.11655

    shoulder_offset = 0.176 #0.220941
    elbow_offset = -0.137 #-0.1719

    # The UR has a very simple workspace: is is s sphere with a cylinder in the
    # center cuff off. The axis of this cylinder is j0. For more info: UR manual.
    working_area_sphere_diameter = 2.65  # max. working area diameter, recommended 2.6
    working_area_cylinder_diameter = 0.19

    def __init__(self):
        super(UR10e, self).__init__()

    def forward_kinematics(self, configuration):
        q = configuration.values[:]
        q[5] += math.pi
        return super(UR10e, self).forward_kinematics(Configuration.from_revolute_values(q))

    def inverse_kinematics(self, tool0_frame_RCS):
        configurations = super(UR10e, self).inverse_kinematics(tool0_frame_RCS)
        for i in range(len(configurations)):
            configurations[i].values[5] -= math.pi
        return configurations


if __name__ == "__main__":

    import math
    from compas_fab.utilities import sign
    from compas.geometry import Frame
    from .kinematics import format_joint_positions
    ur = UR10e()

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
