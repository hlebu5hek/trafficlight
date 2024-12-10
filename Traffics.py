from time import sleep
import asyncio
from typing import override
from threading import Thread

state_change = "state_change"
time_change = "time_change"

class TrafficCtrl(object):
    traffics = []

    def __init__(self, trafficLights):
        self.traffics = trafficLights

        for i, t in enumerate(self.traffics):
            t.SetCtrl(self, i)

    events = [{}]

    def Cancel(self):
        for i in self.traffics:
            i.Cancel()

    def ChangeState(self, traffics):
        for i in traffics:
            self.traffics[i].ChangeState()


    def AddEvent(self, eventName, ind, func):
        if ind >= len(self.traffics):
            for i in range(ind - len(self.traffics) + 1):
                self.events.append({})
        self.events[ind][eventName] = func

    def GetState(self, ind) -> int:
        return self.traffics[ind].GetState()

    def GetWaitTime(self, ind) -> int:
        return self.traffics[ind].GetWaitTime()

    def Invoke(self, ind, event):
        if ind >= len(self.events): return
        if not(event in self.events[ind].keys()): return

        Thread(target=self.events[ind][event]).start()

    def Start(self, ind):
        self.traffics[ind].StartTraffic()

    def Start(self, indxs):
        for ind in indxs:
            self.traffics[ind].StartTraffic()


class TraficLight(object):
    current_singal = 0 #0 = green; 1 = yellow; 2 = red
    red_wait_time = 0
    green_wait_time = 0

    current_wait_time = 0

    task = None
    ctrl = None
    ind = 0

    def SetCtrl(self, ctrl: TrafficCtrl, ind):
        self.ctrl = ctrl

    def Cancel(self):
        if self.task != None:
            if not(self.task.done()):
                self.task.cancel()

    def __init__(self, red_wait_time: int, green_wait_time: int, current_singal: int):
        self.red_wait_time = red_wait_time
        self.green_wait_time = green_wait_time
        self.current_singal = current_singal

    def SetGreenTime(self, green_wait_time: int):
        self.green_wait_time = green_wait_time

    def SetRedTime(self, red_wait_time: int):
        self.red_wait_time = red_wait_time

    def GetState(self) -> int:
        return self.current_singal

    def StartTraffic(self):
        if (self.current_singal == 0): self.current_wait_time = self.green_wait_time
        elif (self.current_singal == 2): self.current_wait_time = self.red_wait_time - 3
        else: self.current_wait_time = 3
        Thread(target=self.Start).start()

    def Start(self):
        self.ctrl.Invoke(self.ind, time_change)
        asyncio.run(self.Wait())

    def GetWaitTime(self) -> int:
        return self.current_wait_time

    async def Wait(self):
        if self.task != None:
            self.task.uncancel()
        self.task = asyncio.create_task(self.Waiting())
        await self.task

    async def Waiting(self):
        t = self.current_wait_time
        for i in range(t, 0, -1):
            await asyncio.sleep(1)
            self.ctrl.Invoke(self.ind, time_change)
            self.current_wait_time -= 1
        self.ChangeState()

    def ChangeState(self):
        if not(self.task.done()):
            self.task.cancel()
        self.current_singal -= 1
        if(self.current_singal < 0): self.current_singal = 2
        self.ctrl.Invoke(self.ind, state_change)
        self.ctrl.Invoke(self.ind, time_change)
        self.StartTraffic()


class WalkTrafficLight(TraficLight):
    @override
    def StartTraffic(self):
        if (self.current_singal == 0):
            self.current_wait_time = self.green_wait_time
        else:
            self.current_wait_time = self.red_wait_time
        Thread(target=self.Start).start()

    @override
    def ChangeState(self):
        if not(self.task.done()):
            self.task.cancel()
        self.current_singal = 2 - self.current_singal
        self.ctrl.Invoke(self.ind, state_change)
        self.StartTraffic()