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



sumoBinary = checkBinary('sumo-gui')
sumoCmd = [sumoBinary, '-c', 'simpleMap.sumocfg']

class TrafficAgent:
    """Defines individual traffic signal behaviour."""

    def __init__(self, lane, gss, yss, gd, yd):
        self._lane = lane
        self._greenDur = gd
        self._yellowDur = yd

        self._greenSignalString = gss
        self._yellowSignalString = yss

    def printQueueStats(self, prevLane):
        """Prints queue data"""
        
        queueLength = traci.lane.getLastStepVehicleNumber(self._lane)
        vehicleLength = traci.lane.getLastStepLength(self._lane)

        queueLength = queueLength * vehicleLength
        avgSpeed = traci.lane.getLastStepMeanSpeed(prevLane._lane) 

        print("QUEUE LENGTH : ", queueLength)
        print("AVG SPEED : ", avgSpeed)

        reward = queueLength - avgSpeed * (self._greenDur + self._yellowDur)
        print("REWARD : ", reward)


    def getSignalLength(self):
        return self._greenDur + self._yellowDur

    def getGreenSignalString(self):
        return self._greenSignalString
    
    def getYellowSignalString(self):
        return self._yellowSignalString


def run():
    greenDur = 30
    yellowDur = 3

    lane0 = TrafficAgent('-gneE1_0', 'rrrGGgrrrrrr', 'rrryyyrrrrrr', greenDur, yellowDur)
    lane1 = TrafficAgent('-gneE3_0', 'rrrrrrGGgrrr', 'rrrrrryyyrrr', greenDur, yellowDur)
    lane2 = TrafficAgent('gneE0_0', 'rrrrrrrrrGGg', 'rrrrrrrrryyy', greenDur, yellowDur)
    lane3 = TrafficAgent('-gneE5_0', 'GGgrrrrrrrrr', 'yyyrrrrrrrrr', greenDur, yellowDur)

    lanes = [lane0, lane1, lane2, lane3]
    laneIndex = 0

    step = 0

    cycle = 0

    currentCycle = 0
    changeState = True
    nextSignal = lane0

    signalDuration = 0
    deadline = 0



    while step < 250:
        traci.simulationStep()

        if changeState:
            # Defines behaviour whenever signals have to be changed.
            signalDuration = greenDur + yellowDur
            print('SIGNAL : ', signalDuration)

            deadline += signalDuration # deadline recorded in terms of total steps.

            print('DEADLINE : ', deadline)

            signalString = nextSignal.getGreenSignalString()
            traci.trafficlight.setRedYellowGreenState("t0", signalString)
            traci.trafficlight.setPhaseDuration("t0", signalDuration - yellowDur)
            print(signalString)
            
            changeState = False # prevent calls to setRedYellowGreenState
        
        elif (cycle == deadline - yellowDur):
            # set yellow phase for three steps before deadline
            signalString = nextSignal.getYellowSignalString()
            traci.trafficlight.setRedYellowGreenState("t0", signalString)
            traci.trafficlight.setPhaseDuration("t0", 3)
            print(signalString)
        
        elif (cycle == deadline - 1):
            changeState = True        
            nextSignal.printQueueStats(lanes[(laneIndex - 1) % 4])
            laneIndex =  (laneIndex + 1) % 4
            nextSignal = lanes[laneIndex]
            print()
        
        cycle += 1
        # print(cycle)
        #END OF SECTION FOR CONTROLLING TRAFFIIC SIGNAL WITH TRACI

        step += 1

    traci.close()

if __name__ == '__main__':
    traci.start(sumoCmd)
    run()