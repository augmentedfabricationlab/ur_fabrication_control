from compas_fab.backends import RosClient
from compas_fab.robots import JointTrajectory, JointTrajectoryPoint, Duration

joint_prefix = "robot_arm_" 
topic_prefix = "/robot/arm/"

JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]
JOINT_NAMES = [joint_prefix+jn for jn in JOINT_NAMES]

COMPLETED = False

def handle(result):
    print(result)
    COMPLETED = True

with RosClient("localhost", 9090) as rosclient:

    joint_trajectory = JointTrajectory(action_name=topic_prefix+"follow_joint_trajectory")
    joint_trajectory.joint_names = JOINT_NAMES

    position_list = [[0, -1.57, -1.57, 0, 0, 0]]
    position_list.append([0.2, -1.57, -1.57, 0, 0, 0])
    position_list.append([0.5, -1.57, -1.2, 0, 0, 0])
    duration_list = [3.0, 7.0, 10.0]

    for position, duration in zip(position_list, duration_list):
        point = JointTrajectoryPoint()
        point.joint_values = position
        point.time_from_start = Duration(duration, 0)
        joint_trajectory.points.append(point)

    tasks = rosclient.follow_joint_trajectory(joint_trajectory, callback=handle)

    while not COMPLETED:
        if KeyboardInterrupt:
            break


