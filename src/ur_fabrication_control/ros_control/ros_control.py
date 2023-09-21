from roslibpy import actionlib
from roslibpy import Service, ServiceRequest, ServiceResponse


actionlib.ActionClient
actionlib.Goal
actionlib.Message

prefix = "robot_arm_" 

JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]
JOINT_NAMES = [prefix+jn for jn in JOINT_NAMES]

JOINT_TRAJECTORY_CONTROLLERS = [
    "scaled_pos_joint_traj_controller",
    "scaled_vel_joint_traj_controller",
    "pos_joint_traj_controller",
    "vel_joint_traj_controller",
    "forward_joint_traj_controller",
]

CARTESIAN_TRAJECTORY_CONTROLLERS = [
    "pose_based_cartesian_traj_controller",
    "joint_based_cartesian_traj_controller",
    "forward_cartesian_traj_controller",
]

CONFLICTING_CONTROLLERS = ["joint_group_vel_controller", "twist_controller"]

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
        

    def send_joint_trajectory(self, joint_configurations):
        self.switch_controller(self.joint_trajectory_controller)
        trajectory_client = actionlib.ActionClient(self.ros_client,
                                                   "{}/follow_joint_trajectory".format(self.joint_trajectory_controller),
                                                   "control_msgs/FollowJointTrajectoryAction")
        
        goal = FollowJointTrajectoryGoal(trajectory_client)
        goal.goal_message.trajectory.joint_names = JOINT_NAMES


    
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


class SwitchControllerRequest(ServiceRequest):
    def __init__(self, values=None):
        super().__init__(values)
        self.update({
            'start_controllers' : [],
            'stop_controllers' : [],
            'strictness' : 1,
            'BEST_EFFORT' : 1,
            'STRICT' : 2,
            'start_asap' : False,
            'timeout' : 5.0
        })

class LoadControllerRequest(ServiceRequest):
    def __init__(self, name, values=None):
        super().__init__(values)
        self.update({
            'name' : name
        })

class ListControllersRequest(ServiceRequest):
    def __init__(self, controller, values=None):
        super().__init__(values)
        self.update({
            'controller' : controller
        })

class FollowJointTrajectoryGoal(actionlib.Goal):
    def __init__(self, action_client):
        goal_message = {
            'trajectory' : None,
            'path_tolerance' : [],
            'goal_tolerance' : [],
            'goal_time_tolerance' : None,
            'error_code' : None,
            'SUCCESSFUL' : 0,
            'INVALID_GOAL' : -1,
            'INVALID_JOINTS' : -2,
            'OLD_HEADER_TIMESTAMP' : -3,
            'PATH_TOLERANCE_VIOLATED' : -4,
            'GOAL_TOLERANCE_VIOLATED' : -5,
            'error_string' : None
        }
        super().__init__(action_client, goal_message)

class JointTrajectory():
    pass

class JointTolerance():
    pass