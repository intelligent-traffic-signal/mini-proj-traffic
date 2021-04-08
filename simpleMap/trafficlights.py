import os
import sys

from generate_routes import TrafficGenerator
from visualization import Visualization


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

MAX_STEPS = 5400
SEED = 10000
NO_CARS = 1000

TrafficGen = TrafficGenerator(MAX_STEPS, NO_CARS)
TrafficGen.generate_routefile(seed=SEED)

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

def collect_waiting_times(waiting_times):
    """
    Retrieve the waiting time of every car in the incoming roads
    """
    incoming_roads = ["E2T", "N2T", "W2T", "S2T"]
    car_list = traci.vehicle.getIDList()
    for car_id in car_list:
        wait_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
        road_id = traci.vehicle.getRoadID(car_id)  # get the road id where the car is located
        if road_id in incoming_roads:  # consider only the waiting times of cars in incoming roads
            waiting_times[car_id] = wait_time
        else:   # not in incoming road
            if car_id in waiting_times: # a car that was tracked has cleared the intersection
                del waiting_times[car_id] 
    total_waiting_time = sum(waiting_times.values())
    return total_waiting_time

def run():
    greenDur = 30
    yellowDur = 3

    lane0 = TrafficAgent('E2T_0', 'rrrGGgrrrrrr', 'rrryyyrrrrrr', greenDur, yellowDur)   # east to west
    lane1 = TrafficAgent('N2T_0', 'rrrrrrGGgrrr', 'rrrrrryyyrrr', greenDur, yellowDur)   # north to south
    lane2 = TrafficAgent('W2T_0', 'rrrrrrrrrGGg', 'rrrrrrrrryyy', greenDur, yellowDur)    # west to east
    lane3 = TrafficAgent('S2T_0', 'GGgrrrrrrrrr', 'yyyrrrrrrrrr', greenDur, yellowDur)   # south to north 

    lanes = [lane0, lane1, lane2, lane3]
    laneIndex = 0

    step = 0

    cycle = 0

    changeState = True
    nextSignal = lane0

    signalDuration = 0
    deadline = 0

    queue_lengths = []
    waiting_times = {}
    old_total_wait = 0
    rewards = []

    visualizer = Visualization('./macro_plots', dpi=96)

    while step < MAX_STEPS:
        traci.simulationStep()

        halt_N = traci.edge.getLastStepHaltingNumber("N2T")
        halt_S = traci.edge.getLastStepHaltingNumber("S2T")
        halt_E = traci.edge.getLastStepHaltingNumber("E2T")
        halt_W = traci.edge.getLastStepHaltingNumber("W2T")

        queue_length = halt_N + halt_S + halt_E + halt_W
        queue_lengths.append(queue_length)

        current_total_wait = collect_waiting_times(waiting_times)
        reward = 0.9*old_total_wait - current_total_wait

        rewards.append(reward)

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
        old_total_wait = current_total_wait

    # PLOT FILES
    visualizer.save_data_and_plot(data=rewards, filename='reward', xlabel='Action step', ylabel='Reward')
    visualizer.save_data_and_plot(data=queue_lengths, filename='queue', xlabel='Step', ylabel='Queue length (vehicles)')


    traci.close()

if __name__ == '__main__':
    traci.start(sumoCmd)
    run()