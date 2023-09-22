from roslibpy import actionlib
from roslibpy import Service

from.builtin_interfaces import Duration
from .trajectory_msgs import JointTrajectory, JointTrajectoryPoint
from .control_msgs import FollowJointTrajectoryGoal
from .controller_manager_msgs import SwitchControllerRequest, ListControllersRequest, LoadControllerRequest

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

JOINT_TRAJECTORY_CONTROLLERS = [
    "scaled_pos_joint_traj_controller",
    "scaled_vel_joint_traj_controller",
    "pos_joint_traj_controller",
    "vel_joint_traj_controller",
    "forward_joint_traj_controller",
]
JOINT_TRAJECTORY_CONTROLLERS = [topic_prefix+jtc for jtc in JOINT_TRAJECTORY_CONTROLLERS]

CARTESIAN_TRAJECTORY_CONTROLLERS = [
    "pose_based_cartesian_traj_controller",
    "joint_based_cartesian_traj_controller",
    "forward_cartesian_traj_controller",
]
CARTESIAN_TRAJECTORY_CONTROLLERS = [topic_prefix+ctc for ctc in CARTESIAN_TRAJECTORY_CONTROLLERS]


CONFLICTING_CONTROLLERS = ["joint_group_vel_controller", "twist_controller"]
CONFLICTING_CONTROLLERS = [topic_prefix+cc for cc in CONFLICTING_CONTROLLERS]

class URROSControl():
    def __init__(self, ros_client):
        self.ros_client = ros_client

        self.switch_srv = Service(ros_client,
                                  "controller_manager/switch_controller",
                                  "controller_manager_msgs/srv/SwitchController")
        self.load_srv = Service(ros_client,
                                "controller_manager/load_controller",
                                "controller_manager_msgs/srv/LoadController")
        
        self.list_srv = Service(ros_client,
                                "controller_manager/list_controllers",
                                "controller_manager_msgs/srv/ListControllers")
        
        self.joint_trajectory_controller = JOINT_TRAJECTORY_CONTROLLERS[0]
        self.cartesian_trajectory_controller = CARTESIAN_TRAJECTORY_CONTROLLERS[0]
        

    def send_joint_trajectory_test(self):
        self.switch_controller(self.joint_trajectory_controller)
        trajectory_client = actionlib.ActionClient(self.ros_client,
                                                   "{}/follow_joint_trajectory".format(self.joint_trajectory_controller),
                                                   "control_msgs/FollowJointTrajectoryAction")
        
        goal = FollowJointTrajectoryGoal(trajectory_client)
        goal.goal_message.trajectory.joint_names = JOINT_NAMES

        position_list = [[0, -1.57, -1.57, 0, 0, 0]]
        position_list.append([0.2, -1.57, -1.57, 0, 0, 0])
        position_list.append([0.5, -1.57, -1.2, 0, 0, 0])
        duration_list = [3.0, 7.0, 10.0]

        for position, duration in zip(position_list, duration_list):
            point = JointTrajectoryPoint()
            point.position = position
            point.time_from_start = Duration(duration)
            goal.goal_message.trajectory.points.append(point)
        
        # trajectory_client.add_goal(goal) # does not seem nessecary?
        goal.send()
        result = goal.wait(10)
        trajectory_client.dispose()
        print(result)
    
    def send_joint_trajectory(self, joint_trajectory):
        self.switch_controller(self.joint_trajectory_controller)
        trajectory_client = actionlib.ActionClient(self.ros_client,
                                                   "{}/follow_joint_trajectory".format(self.joint_trajectory_controller),
                                                   "control_msgs/FollowJointTrajectoryAction")
        
        goal = FollowJointTrajectoryGoal(trajectory_client)
        goal.goal_message.trajectory.joint_names = JOINT_NAMES

        position_list = [[0, -1.57, -1.57, 0, 0, 0]]
        position_list.append([0.2, -1.57, -1.57, 0, 0, 0])
        position_list.append([0.5, -1.57, -1.2, 0, 0, 0])
        duration_list = [3.0, 7.0, 10.0]

        for position, duration in zip(position_list, duration_list):
            point = JointTrajectoryPoint()
            point.position = position
            point.time_from_start = Duration(duration)
            goal.goal_message.trajectory.points.append(point)
        
        # trajectory_client.add_goal(goal) # does not seem nessecary?
        goal.send()
        result = goal.wait(10)
        trajectory_client.dispose()
        print(result)

    def switch_controller(self, target_controller):
        other_controllers = (
            JOINT_TRAJECTORY_CONTROLLERS
            + CARTESIAN_TRAJECTORY_CONTROLLERS
            + CONFLICTING_CONTROLLERS
        )

        other_controllers.remove(target_controller)

        srv = ListControllersRequest()
        response = self.list_srv.call(srv)
        for controller in response.controller:
            if controller.name == target_controller and controller.state == "running":
                return
        
        srv = LoadControllerRequest()
        srv.name = target_controller
        self.load_srv(srv)

        srv = SwitchControllerRequest()
        srv.stop_controllers = other_controllers
        srv.start_controllers = [target_controller]
        srv.strictness = SwitchControllerRequest.BEST_EFFORT
        self.switch_srv(srv)