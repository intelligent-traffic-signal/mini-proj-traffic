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

e3Detector_0 = 0
e3Detector_1 = 0
e3Detector_2 = 0
e3Detector_3 = 0

while step < 300:
    traci.simulationStep()

    # The four variables increment by the number of vehicles that passed through 
    # in the last step, and reset every cycle
    # NOTE: TODO: it is incrementing too fast; fix tomorrow
    # Keep a check for when to increment
    e3Detector_0 += traci.multientryexit.getLastStepVehicleNumber('e3Detector_0')
    e3Detector_1 += traci.multientryexit.getLastStepVehicleNumber('e3Detector_1')
    e3Detector_2 += traci.multientryexit.getLastStepVehicleNumber('e3Detector_2')
    e3Detector_3 += traci.multientryexit.getLastStepVehicleNumber('e3Detector_3')
    

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
        print('e3Detector_0', e3Detector_0)
        print('e3Detector_1', e3Detector_1)
        print('e3Detector_2', e3Detector_2)
        print('e3Detector_3', e3Detector_3)
        print()

        # Reset cycle and detector values
        e3Detector_0, e3Detector_1, e3Detector_2, e3Detector_3 = 0, 0, 0, 0
        cycle = 0

    cycle += 1
    #END OF SECTION FOR CONTROLLING TRAFFIC SIGNAL WITH TRACI
    
    step += 1

traci.close()