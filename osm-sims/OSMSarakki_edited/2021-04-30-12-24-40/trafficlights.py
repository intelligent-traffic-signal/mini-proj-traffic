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


MAX_STEPS = 5400
SEED = 10001
NO_CARS = 1000
UNIFORM = (SEED % 3) == 0
MIN_TIME = 3
MAX_TIME = 51

# Generate route file
TrafficGen = TrafficGenerator(MAX_STEPS, NO_CARS)
TrafficGen.generate_routefile(seed=SEED)

if (SEED % 3) == 0:
    visualizer = Visualization('./macro_plots_uniform', dpi=96)
elif (SEED % 3) == 1:
    visualizer = Visualization('./macro_plots_ns', dpi=96)
else:
    visualizer = Visualization('./macro_plots_ew', dpi=96)

class TrafficAgent:
    """Defines individual traffic signal behaviour."""

    def __init__(self, lane_a, lane_b, gss, yss):
        self._strategySet = list(range(MIN_TIME, MAX_TIME)) # Action space defined as discrete time intervals; base idea can be tweaked. 
        self._strategyCount = len(self._strategySet)

        self._probabilitySet = [1 / self._strategyCount for i in range(self._strategyCount)]
        
        self._lane_a = lane_a
        self._lane_b = lane_b

        self._greenSignalString = gss
        self._yellowSignalString = yss

    def updateProbabilitySet(self, prevLane):
        """Defines feedback mechanism. Probability space updated according to backlog in lane."""
        
        queueLength_a = traci.lane.getLastStepHaltingNumber(self._lane_a)
        vehicleLength_a = traci.lane.getLastStepLength(self._lane_a)

        queueLength_b = traci.lane.getLastStepHaltingNumber(self._lane_b)
        vehicleLength_b = traci.lane.getLastStepLength(self._lane_b)

        queueLength = max(queueLength_a * vehicleLength_a, queueLength_b * vehicleLength_b)
        avgSpeed = 22.5

        print("QUEUE LENGTH : ", queueLength)
        print("AVG SPEED : ", avgSpeed)

        rewardSet = [abs(queueLength - avgSpeed * self._strategySet[i]) for i in range(self._strategyCount)]
        print(rewardSet)

        reward = min(rewardSet)
        self._probabilitySet = [1 if rewardSet[i] == reward else 0 for i in range(self._strategyCount)]
        print(self._probabilitySet)

    def getSignalLength(self):
        for i in range(self._strategyCount):
            if self._probabilitySet[i]:
                return self._strategySet[i]

    def getGreenSignalString(self):
        return self._greenSignalString
    
    def getYellowSignalString(self):
        return self._yellowSignalString

lane0 = TrafficAgent('S2T_0', 'S2T_1', 'GGGgrrrrrrrrrrrrrr', 'yyyyrrrrrrrrrrrrrr')
lane1 = TrafficAgent('E2T_0', 'E2T_1', 'rrrrGGGggrrrrrrrrr', 'rrrryyyyyrrrrrrrrr')
lane2 = TrafficAgent('N2T_0', 'N2T_1', 'rrrrrrrrrGGGgrrrrr', 'rrrrrrrrryyyyrrrrr')
lane3 = TrafficAgent('W2T_0', 'W2T_1', 'rrrrrrrrrrrrrGGGgg', 'rrrrrrrrrrrrryyyyy')

lanes = [lane0, lane1, lane2, lane3]
laneIndex = 0

sumoBinary = checkBinary('sumo-gui')
sumoCmd = [sumoBinary, '-c', 'osm.sumocfg', '--queue-output', 'queuedata.xml', '--log', 'LOGFILE']

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

step = 0
greenDur = 30
yellowDur = 3
cycle = 0

currentCycle = 0
changeState = True
nextSignal = lane0

signalDuration = 0
deadline = 0

queue_lengths = []
waiting_times = {}
old_total_wait = 0
rewards = []

traci.start(sumoCmd)

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
        signalDuration = nextSignal.getSignalLength()
        print('SIGNAL : ', signalDuration)

        deadline += signalDuration # deadline recorded in terms of total steps.

        print('DEADLINE : ', deadline)

        signalString = nextSignal.getGreenSignalString()
        traci.trafficlight.setRedYellowGreenState("T", signalString)
        traci.trafficlight.setPhaseDuration("T", signalDuration - 3)
        print(signalString)
        
        changeState = False # prevent calls to setRedYellowGreenState
    
    elif (cycle == deadline - 3):
        # set yellow phase for three steps before deadline
        signalString = nextSignal.getYellowSignalString()
        traci.trafficlight.setRedYellowGreenState("T", signalString)
        traci.trafficlight.setPhaseDuration("T", 3)
        print(signalString)
    
    elif (cycle == deadline - 1):
        changeState = True

        # update the next signal agent with current information
        nextSignal.updateProbabilitySet(lanes[(laneIndex - 1) % 4])
        
        laneIndex =  (laneIndex + 1) % 4
        nextSignal = lanes[laneIndex]
    
    cycle += 1
    step += 1
    old_total_wait = current_total_wait

    #END OF SECTION FOR CONTROLLING TRAFFIIC SIGNAL WITH TRACI

    

# PLOT FILES
visualizer.save_data_and_plot(data=rewards, filename='reward', xlabel='Action step', ylabel='Reward')
visualizer.save_data_and_plot(data=queue_lengths, filename='queue', xlabel='Step', ylabel='Queue length (vehicles)')


traci.close()