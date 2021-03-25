import os
import sys

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

import random

class TrafficAgent:
    """Defines individual traffic signal behaviour."""

    def __init__(self, lane, gss, yss):
        self._strategySet = list(range(5, 31, 2)) # Action space defined as discrete time intervals; base idea can be tweaked. 
        self._strategyCount = len(self._strategySet)

        self._probabilitySet = [1 / self._strategyCount for i in range(self._strategyCount)]
        
        self._lane = lane

        self._greenSignalString = gss
        self._yellowSignalString = yss

    def updateProbabilitySet(self):
        """Defines feedback mechanism. Probability space updated according to backlog in lane."""
        queueLength = traci.lane.getLastStepVehicleNumber(self._lane)
        avgSpeed = 13.89 # Arbitrary set based on simpleMap.net.xml

        rewardSet = [(queueLength * 5 - avgSpeed * self._strategySet[i]) for i in range(self._strategyCount)]
        
        totalRwd = sum(rewardSet)
        for i in range(self._strategyCount):
            rewardSet[i] /= totalRwd

        self._probabilitySet = rewardSet

    def getSignalLength(self):
        """Update probability space to allow uncertainty."""
        return random.choices(self._strategySet, weights=self._probabilitySet, k=1)[0]

    def getGreenSignalString(self):
        return self._greenSignalString
    
    def getYellowSignalString(self):
        return self._yellowSignalString

lane0 = TrafficAgent('-gneE1_0', 'rrrGGgrrrrrr', 'rrryyyrrrrrr')
lane1 = TrafficAgent('-gneE3_0', 'rrrrrrGGgrrr', 'rrrrrryyyrrr')
lane2 = TrafficAgent('gneE0_0', 'rrrrrrrrrGGg', 'rrrrrrrrryyy')
lane3 = TrafficAgent('-gneE5_0', 'GGgrrrrrrrrr', 'yyyrrrrrrrrr')

lanes = [lane0, lane1, lane2, lane3]
laneIndex = 0

sumoBinary = checkBinary('sumo-gui')
sumoCmd = [sumoBinary, '-c', 'simpleMap.sumocfg', '--additional-files', 'add_macro.xml']

step = 0
greenDur = 30
yellowDur = 3
cycle = 0

currentCycle = 0
changeState = True
nextSignal = lane0

signalDuration = 0
deadline = 0

traci.start(sumoCmd)

while step < 250:
    traci.simulationStep()

    if changeState:
        # Defines behaviour whenever signals have to be changed.
        signalDuration = nextSignal.getSignalLength()
        print('SIGNAL : ', signalDuration)

        deadline += signalDuration # deadline recorded in terms of total steps.

        print('DEADLINE : ', deadline)

        signalString = nextSignal.getGreenSignalString()
        traci.trafficlight.setRedYellowGreenState("t0", signalString)
        traci.trafficlight.setPhaseDuration("t0", signalDuration - 3)
        print(signalString)
        
        changeState = False # prevent calls to setRedYellowGreenState
    
    elif (cycle == deadline - 3):
        # set yellow phase for three steps before deadline
        signalString = nextSignal.getYellowSignalString()
        traci.trafficlight.setRedYellowGreenState("t0", signalString)
        traci.trafficlight.setPhaseDuration("t0", 3)
        print(signalString)
    
    elif (cycle == deadline - 1):
        changeState = True
        laneIndex =  (laneIndex + 1) % 4
        nextSignal = lanes[laneIndex]

        # update the next signal agent with current information
        nextSignal.updateProbabilitySet()
    
    cycle += 1
    # print(cycle)
    #END OF SECTION FOR CONTROLLING TRAFFIIC SIGNAL WITH TRACI

    step += 1

traci.close()