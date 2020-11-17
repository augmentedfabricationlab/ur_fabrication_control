'''
Created on 11.10.2017

@author: rustr
'''

import Grasshopper as gh

def gh_component_timer(ghenv, run, interval):
    if interval <= 0: interval = 1
    ghComp = ghenv.Component
    ghDoc = ghComp.OnPingDocument()
    def callBack(ghDoc):
        ghComp.ExpireSolution(False)
    if run:
        ghDoc.ScheduleSolution(interval, gh.Kernel.GH_Document.GH_ScheduleDelegate(callBack))