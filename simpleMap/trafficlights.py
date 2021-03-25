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
    def __init__(self, lane, gss, yss):
        """Defining a set of actions as the time the signal should be on in terms of discrete time intervals."""
        self._strategySet = list(range(5, 31, 2))
        self._strategyCount = len(self._strategySet)

        self._probabilitySet = [1 / self._strategyCount for i in range(self._strategyCount)]
        
        self._lane = lane

        self._greenSignalString = gss
        self._yellowSignalString = yss

    def updateProbabilitySet(self):
        queueLength = traci.lane.getLastStepVehicleNumber(self._lane)
        avgSpeed = 13.89 # Arbitrary set based on simpleMap.net.xml

        rewardSet = [(queueLength - avgSpeed * self._strategySet[i]) for i in range(self._strategyCount)]
        
        if min(rewardSet) < 0:
            minRwd = min(rewardSet)
            for i in range(self._strategyCount):
                rewardSet[i] -= minRwd
        
        totalRwd = sum(rewardSet)
        for i in range(self._strategyCount):
            rewardSet[i] /= totalRwd
        
        self._probabilitySet = rewardSet

    def getSignalLength(self):
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
sumoCmd = [sumoBinary, '-c', 'simpleMap.sumocfg', '--additional-files', 'additional.xml']

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

    #The below section of code can be commented if traffic light control to be done by states already defines in netedit
    #If below section left uncommented the traffic signal control done through TraCi
    #Alternatively, all the setRedYellowGreenState calls could be replaced by setPhase("t0", index) where index is 0,1,2,3,4 to produce same functionality
    """
    if cycle in range(greenDur):
        traci.trafficlight.setRedYellowGreenState("t0", "rrrGGgrrrrrr")
        traci.trafficlight.setPhaseDuration("t0", greenDur)
    elif cycle in range(greenDur+yellowDur):
        traci.trafficlight.setRedYellowGreenState("t0", "rrryyyrrrrrr")
        traci.trafficlight.setPhaseDuration("t0", yellowDur)  
    elif cycle in range(2*greenDur+yellowDur):
        traci.trafficlight.setRedYellowGreenState("t0", "rrrrrrGGgrrr")
        traci.trafficlight.setPhaseDuration("t0", greenDur)
    elif cycle in range(2*greenDur+2*yellowDur):
        traci.trafficlight.setRedYellowGreenState("t0", "rrrrrryyyrrr")
        traci.trafficlight.setPhaseDuration("t0", yellowDur)  
    elif cycle in range(3*greenDur+2*yellowDur):
        traci.trafficlight.setRedYellowGreenState("t0", "rrrrrrrrrGGg")
        traci.trafficlight.setPhaseDuration("t0", greenDur)
    elif cycle in range(3*greenDur+3*yellowDur):
        traci.trafficlight.setRedYellowGreenState("t0", "rrrrrrrrryyy")
        traci.trafficlight.setPhaseDuration("t0", yellowDur) 
    elif cycle in range(4*greenDur+3*yellowDur):
        traci.trafficlight.setRedYellowGreenState("t0", "GGgrrrrrrrrr")
        traci.trafficlight.setPhaseDuration("t0", greenDur)
    elif cycle in range(4*greenDur+4*yellowDur):
        traci.trafficlight.setRedYellowGreenState("t0", "yyyrrrrrrrrr")
        traci.trafficlight.setPhaseDuration("t0", yellowDur) 
    else:
        cycle = 0
    """

    if changeState:
        signalDuration = nextSignal.getSignalLength()
        print('SIGNAL : ', signalDuration)

        deadline += signalDuration

        print('DEADLINE : ', deadline)

        signalString = nextSignal.getGreenSignalString()
        traci.trafficlight.setRedYellowGreenState("t0", signalString)
        traci.trafficlight.setPhaseDuration("t0", signalDuration - 3)
        print(signalString)
        
        changeState = False
    
    elif (cycle == deadline - 3):
        signalString = nextSignal.getYellowSignalString()
        traci.trafficlight.setRedYellowGreenState("t0", signalString)
        traci.trafficlight.setPhaseDuration("t0", 3)
        print(signalString)
    
    elif (cycle == deadline - 1):
        changeState = True
        laneIndex =  (laneIndex + 1) % 4
        nextSignal = lanes[laneIndex]
    
    cycle += 1
    # print(cycle)
    #END OF SECTION FOR CONTROLLING TRAFFIIC SIGNAL WITH TRACI

    step += 1

traci.close()