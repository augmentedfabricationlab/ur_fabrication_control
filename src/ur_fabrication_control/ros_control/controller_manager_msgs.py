from roslibpy import ServiceRequest

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