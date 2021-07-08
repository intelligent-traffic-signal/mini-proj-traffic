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
SEED = 10003
NO_CARS = 1000
UNIFORM = (SEED % 3) == 0
MIN_TIME = 5
MAX_TIME = 31
GUI = False

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

    def __init__(self, lane, ogLane, gss, yss):
        self._strategySet = list(range(MIN_TIME, MAX_TIME)) # Action space defined as discrete time intervals; base idea can be tweaked. 
        self._strategyCount = len(self._strategySet)

        self._probabilitySet = [1 / self._strategyCount for i in range(self._strategyCount)]
        
        self._lane = lane
        self._prevLane = ogLane

        self._greenSignalString = gss
        self._yellowSignalString = yss

    def updateProbabilitySet(self, prevLane):
        """Defines feedback mechanism. Probability space updated according to backlog in lane."""
        
        queueLength = traci.lane.getLastStepVehicleNumber(self._lane)
        # vehicleLength = traci.lane.getLastStepLength(self._lane)

        print("NO VEHICLES: ", queueLength)

        queueLength = queueLength * 7
        # avgSpeed = 5 # traci.lane.getLastStepMeanSpeed(self._prevLane) 

        print("QUEUE LENGTH : ", queueLength)
        # print("AVG SPEED : ", avgSpeed)

        rewardSet = [abs(queueLength - self._strategySet[i]) for i in range(self._strategyCount)]
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

lane0 = TrafficAgent('E2T_0', 'T2S_0', 'rrrGGgrrrrrr', 'rrryyyrrrrrr')   # east to west
lane1 = TrafficAgent('N2T_0', 'T2E_0', 'rrrrrrGGgrrr', 'rrrrrryyyrrr')   # north to south
lane2 = TrafficAgent('W2T_0', 'T2N_0', 'rrrrrrrrrGGg', 'rrrrrrrrryyy')   # west to east
lane3 = TrafficAgent('S2T_0', 'T2W_0', 'GGgrrrrrrrrr', 'yyyrrrrrrrrr')   # south to north

lanes = [lane3, lane0, lane1, lane2]
laneIndex = 0

if GUI == False:
    sumoBinary = checkBinary('sumo')
else:
    sumoBinary = checkBinary('sumo-gui')

sumoCmd = [sumoBinary, '-c', 'simpleMap.sumocfg', '--additional-files', 'add_macro.xml', '--queue-output', 'queuedata.xml']

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
visualizer.save_data_and_plot(data=queue_lengths, filename='queue', xlabel='Timestep', ylabel='Queue length (vehicles)')


traci.close()