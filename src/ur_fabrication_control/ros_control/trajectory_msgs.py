
from roslibpy import Message, Header

class JointTrajectory(Message):
    def __init__(self, values=None):
        super().__init__(values)
        self.update({
            'header' : Header(),
            'joint_names' : [],
            'points' : []
        })

class JointTrajectoryPoint(Message):
    def __init__(self, values=None):
        super().__init__(values)
        self.update({
            'positions' : [],
            'velocities' : [],
            'accelerations' : [],
            'effort' : [],
            'time_from_start' : None
        })