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
sumoCmd = [sumoBinary, '-c', 'simpleMap.sumocfg', '--additional-files', 'additional.xml']

step = 0
greenDur = 30
yellowDur = 3
cycle = 0
traci.start(sumoCmd)

while step < 250:
    traci.simulationStep()

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
        cycle = 0

    cycle += 1
    #END OF SECTION FOR CONTROLLING TRAFFIIC SIGNAL WITH TRACI

    step += 1

traci.close()