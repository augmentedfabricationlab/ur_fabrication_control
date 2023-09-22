from roslibpy import Message
from roslibpy import actionlib
from .trajectory_msgs import JointTrajectory

class FollowJointTrajectoryGoal(actionlib.Goal):
    def __init__(self, action_client):
        goal_message = {
            'trajectory' : JointTrajectory(),
            'path_tolerance' : [],
            'goal_tolerance' : [],
            'goal_time_tolerance' : 0,
            'error_code' : None,
            'SUCCESSFUL' : 0,
            'INVALID_GOAL' : -1,
            'INVALID_JOINTS' : -2,
            'OLD_HEADER_TIMESTAMP' : -3,
            'PATH_TOLERANCE_VIOLATED' : -4,
            'GOAL_TOLERANCE_VIOLATED' : -5,
            'error_string' : ''
        }
        super().__init__(action_client, goal_message)

class JointTolerance(Message):
    def __init__(self, name = "jointtolerance", position=0, velocity=0, acceleration=0, values=None):
        super().__init__(values)
        self.update({
            'name' : name,
            'position' : position,
            'velocity' : velocity,
            'acceleration' : acceleration
        })
