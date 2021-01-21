from __future__ import absolute_import

import math

#from compas_fab.utilities import sign
#from compas_fab.robots import Configuration #from ..robot import BaseConfiguration
from ur_fabrication_control.ur.kinematics.utilities import sign
from ur_fabrication_control.ur.configuration import Configuration


def format_joint_positions(joint_positions_a, joint_positions_b = [0,0,0,0,0,0]):
    """Add or subtract 2*pi to the joint positions a, so that they have the
    least difference to joint positions b.
    """

    new_joint_positions = []
    for a1, b in zip(joint_positions_a, joint_positions_b):
        a2 = a1 - (math.pi * 2 * sign(a1))
        a3 = a1 + (math.pi * 2 * sign(a1))

        jp = [a1, a2, a3]
        diffs = [math.fabs(a - b) for a in jp]
        min_idx = diffs.index(min(diffs))
        new_joint_positions.append(jp[min_idx])
    return new_joint_positions

def smallest_joint_pose(joint_positions):
    """Add or subtract 2*pi to the joint positions a, so that they have the
    smallest value.
    """
    return format_joint_positions(joint_positions)


def calculate_configurations_for_path(frames, robot, current_positions = []):
    """Calculate possible configurations for a path.

    Args:
        frames (Frame): the path described with frames

    Returns:
        configurations: list of list of float
    """

    configurations = []

    for i, frame in enumerate(frames):
        configs = robot.inverse_kinematics(frame)
        #qsols = [c.joint_values for c in configs]
        qsols = [c.values for c in configs]
        if not len(qsols):
            return []
        if i == 0:
            if len(current_positions):
                qsols_formatted = []
                for jp_a in qsols:
                    jp_a_formatted = format_joint_positions(jp_a, current_positions)
                    qsols_formatted.append(jp_a_formatted)
                configurations.append(qsols_formatted)
            else:
                configurations.append(qsols)
        else:
            previous_qsols = configurations[-1][:]
            qsols_sorted = []
            for jp_b in previous_qsols:
                diffs = []
                qsols_formatted = []
                for jp_a in qsols:
                    jp_a_formatted = format_joint_positions(jp_a, jp_b)
                    qsols_formatted.append(jp_a_formatted)
                    diffs.append(sum([math.fabs(qa - qb) for qa, qb in zip(jp_a_formatted, jp_b)]))
                selected_idx = diffs.index(min(diffs))
                qsols_sorted.append(qsols_formatted[selected_idx])
            configurations.append(qsols_sorted)

    configurations = list(zip(*configurations))

    for i in range(len(configurations)):
        configurations[i] = list(configurations[i])
        for j, q in enumerate(configurations[i]):
            #configurations[i][j] = BaseConfiguration.from_joints(q)
            configurations[i][j] = Configuration.from_revolute_values(q)

    return configurations
