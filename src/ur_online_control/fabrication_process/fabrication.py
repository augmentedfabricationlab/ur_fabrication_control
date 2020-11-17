'''
. . . . . . . . . . . . . . . . . . . . . . 
.                                         .
.   <<  <<><><>  <<      ><  <<      ><   .
.   <<  <<       < ><   ><<  < ><   ><<   .
.   <<  <<><><>  << >< > ><  << >< > ><   .  
.   <<  <<       <<  ><  ><  <<  ><  ><   .
.   <<  <<       <<      ><  <<      ><   .
.   <<  <<       <<      ><  <<      ><   .
.                                         .
.             GKR 2016/17                 .
. . . . . . . . . . . . . . . . . . . . . .

Created on 29.01.2017

@author: kathrind
'''

from threading import Thread, Condition


class Fabrication:
    
    def __init__(self):
        self.iterations = 0
        
        self.log_messages = []
        self.log_messages_length = 10
        
        self.run_fabrication_flag = True

        self.tasks = []
        self.current_task = None
        
        self.reset()
        
        self.current_base_plane = None
        self.current_base_pose_cartesian = None

        self.server = None
    
    def check_base_estimation(self, new_base_plane):
        
        if self.current_base_plane:
            if self.current_base_plane.Origin.DistanceTo(new_base_plane.Origin) > 20:
                return False
        return True
        
    def set_tasks(self, tasks):
        self.tasks = tasks

    def clear_tasks(self):
        self.tasks = []

    def reset(self):
        self.run_fabrication_flag = True
        self.t = Thread(target = self.run)
        self.t.daemon = True  # OK for main to exit even if instance is still running
        self.t.paused = True  # start out paused
        self.t.state = Condition()
        
    def resume(self):
        with self.t.state:
            self.t.paused = False
            self.t.state.notify()  # unblock self if waiting

    def pause(self):
        with self.t.state:
            self.t.paused = True  # make self block and wait
    
    def start(self, server=None):
        self.server = server
        self.t.start()
    
    def join(self):
        self.t.join()
    
    def is_paused(self):
        return self.t.paused
    
    def is_alive(self):
        return self.t.is_alive()
    
    def run(self):
        self.resume() 
        while len(self.tasks):
            with self.t.state:
                if self.t.paused:
                    self.t.state.wait() # block until notified
                
                if self.run_fabrication_flag == False:
                    break
                
                self.current_task = self.tasks[0]
                
                ok = self.perform_task(self.current_task)

                if ok:
                    #self.current_task.set_built_state(True)
                    self.tasks.pop(0)
                    self.log("POP TASK OFF THE LIST...")
                    
                else:
                    self.log("PAUSING FABRICATION...")
                    self.pause()
                
            self.iterations += 1
            
            if self.run_fabrication_flag == False:
                break
                
        self.log("ALL TASKS DONE")


    def perform_task(self, task):
        """ This method has to be overwitten ... """
        self.log("TASK START: ---->>>>>")
        ok = True
        # do something
        if not ok:
            return False
        
        self.log("----<<<<< TASK FINISHED")
        return True
    
    def log(self, msg):
        self.log_messages.append("FABRICATION: " + str(msg))
        if len(self.log_messages) > self.log_messages_length:
            self.log_messages = self.log_messages[-self.log_messages_length:] 
    
    def get_log_messages(self):       
        return "\n".join(self.log_messages) 




