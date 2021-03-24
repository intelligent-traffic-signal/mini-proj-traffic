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

step = 0
greenDur = 30
yellowDur = 3
cycle = 0
traci.start(sumoCmd)

# print(traci.getIDList())
# print(dir(traci.inductionloop))

class SensorData:
    def __init__(self, id):
        self.id = id
        self.prev_veh = ''      # Previous vehicle sensed (ID)
        self.cur_veh = ''       # Current vehicle sensed (ID)
        self.throughput = 0     # Throughput every cycle

    def update(self):
        self.cur_veh = traci.multientryexit.getLastStepVehicleIDs(self.id)
        if self.cur_veh:
            self.cur_veh = self.cur_veh[0]
        else:
            self.cur_veh = ''

        if self.prev_veh != self.cur_veh:
            self.prev_veh = self.cur_veh
            self.throughput += traci.multientryexit.getLastStepVehicleNumber(self.id)

    def reset(self):
        self.throughput = 0     # Throughput every cycle

    def __str__(self):
        return str(self.id) + ', ' + str(self.throughput)

    def getThroughput(self):
        return self.throughput


e3Detector_0 = SensorData('e3Detector_0')
e3Detector_1 = SensorData('e3Detector_1')
e3Detector_2 = SensorData('e3Detector_2')
e3Detector_3 = SensorData('e3Detector_3')


while step < 600:
    traci.simulationStep()

    # The four variables store sensor data and update 
    # every step, reset every cycle
    
    e3Detector_0.update()
    e3Detector_1.update()
    e3Detector_2.update()
    e3Detector_3.update()

    #The below section of code can be commented if traffic light control to be done by states already defines in netedit
    #If below section left uncommented the traffic signal control done through TraCi
    #Alternatively, all the setRedYellowGreenState calls could be replaced by setPhase("t0", index) where index is 0,1,2,3,4 to produce same functionality
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
        # The print statements run after every cycle of RR (throughput)
        print('Cycle:', cycle)
        print(e3Detector_0)
        print(e3Detector_1)
        print(e3Detector_2)
        print(e3Detector_3)
        
        print()

        # Reset cycle and detector values
        e3Detector_0.reset()
        e3Detector_1.reset()
        e3Detector_2.reset()
        e3Detector_3.reset()

        cycle = 0

    cycle += 1
    #END OF SECTION FOR CONTROLLING TRAFFIC SIGNAL WITH TRACI
    
    step += 1

traci.close()