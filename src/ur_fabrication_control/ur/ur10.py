from __future__ import absolute_import

import math

from ur_online_control.ur.ur import UR


class UR10(UR):
    """The UR 10 robot class.

    Manual link:
    #define UR10_PARAMS
    https://github.com/ros-industrial/universal_robot/blob/kinetic-devel/ur_kinematics/src/ur_kin.cpp
    in meters
    """

    # define UR10_PARAMS
    d1 =  0.1273
    a2 = -0.612
    a3 = -0.5723
    d4 =  0.163941
    d5 =  0.1157
    d6 =  0.0922

    shoulder_offset = 0.220941
    elbow_offset = -0.1719

    # The UR has a very simple workspace: is is s sphere with a cylinder in the
    # center cuff off. The axis of this cylinder is j0. For more info: UR manual.
    working_area_sphere_diameter = 2.65  # max. working area diameter, recommended 2.6
    working_area_cylinder_diameter = 0.190

    def __init__(self):
        super(UR10, self).__init__()

    def forward_kinematics(self, configuration):
        q = configuration.joint_values[:]
        q[5] += math.pi
        return super(UR10, self).forward_kinematics(BaseConfiguration.from_joints(q))

    def inverse_kinematics(self, tool0_frame_RCS):
        configurations = super(UR10, self).inverse_kinematics(tool0_frame_RCS)
        for q in configurations:
            print(q)
        for i in range(len(configurations)):
            configurations[i].values[5] -= math.pi
        return configurations


def main():
    ur10 = UR10()
    q = [-0.4817717618752444, 2.900620189456401, 4.466606474692679, 3.6283476234151966, 1.5707963267948974, 5.194160742259934]
    q = [0, 0, 0, 0, 0, 0]
    R0, R1, R2, R3, R4, R5 = ur10.get_forward_transformations(q)
    print(ur10.forward_kinematics(q))
    tool0_frame = ur10.tool0_frame.transform(R5, copy=True)
    print(tool0_frame)


if __name__ == "__main__":
    from compas.geometry import Frame
    from .kinematics.path_calculation import smallest_joint_pose

    ur = UR10()

    q = [4.6733, -3.39529, 1.5404, -2.90962, -1.58137, 1.59137]
    pose = [-0.206258, -0.865946, 0.60626, 0.037001, -0.044931, 1.55344]

    pose = [-0.576673, -0.717359, 0.419691, -1.41669, -0.88598900000000003, 0.96527600000000002]
    q = [4.32717, -3.57284, 1.62216, -2.58119, -0.00038495899999999998, 1.45664]
    print("q: {0}".format(smallest_joint_pose(q)))
    f = Frame.from_pose_axis_angle_vector(pose)
    print("f: {0}".format(f))

    R0, R1, R2, R3, R4, R5 = ur.get_forward_transformations(q)
    f = ur.get_transformed_tool_frames(R5)[0]
    print("f ?: {0}".format(f))

    #f = ur.forward_kinematics(q)
    #print("f 1: {0}".format(f))
    q = ur.inverse_kinematics(f)


    print()
    for x in q:
        print(smallest_joint_pose(x))
    print()

    f = Frame.from_pose_axis_angle_vector(pose)
