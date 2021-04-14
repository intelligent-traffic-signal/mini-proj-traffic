from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

"""
AVAILABLE PARAMETERS
--------- ----------
    sampledSeconds : The number of vehicles that are present on the edge/lane in each second summed up over the measurement interval 
        (may be subseconds if a vehicle enters/leaves the edge/lane).

    traveltime : Time needed to pass the edge/lane, note that this is just an estimation based on the mean speed, not the exact time 
        the vehicles needed. The value is based on the time needed for the front of the vehicle to pass the edge.

    overlapTraveltime : Time needed to pass the edge/lane completely, note that this is just an estimation based on the mean speed, not 
        the exact time the vehicles needed. The value is based on the time any part of the vehicle was the edge.

    density : Vehicle density on the lane/edge (#veh/km).

    occupancy : Occupancy of the edge/lane in %. A value of 100 would indicate vehicles standing bumper to bumper on the whole edge (minGap=0).

    waitingTime : The total number of seconds vehicles were considered halting (speed < speedThreshold). Summed up over all vehicles.

    timeLoss : The total number of seconds vehicles lost due to driving slower than desired (summed up over all vehicles).

    speed : The mean speed on the edge/lane within the reported interval.

    departed : The number of vehicles that have been emitted onto the edge/lane within the described interval.

    arrived : The number of vehicles that have finished their route on the edge lane.

    entered	: The number of vehicles that have entered the edge/lane by moving from upstream.

    left : The number of vehicles that have left the edge/lane by moving downstream.

    laneChangedFrom	: The number of vehicles that changed away from this lane.

    laneChangedTo : The number of vehicles that changed to this lane.
"""

def getTrafData(filename, identifier, identifier_id, parameter):
    # NOTE: Although './trafficinfo_detailed.xml' has been used, in case of macroscopic parameters, change file to './trafficinfo.xml'
    with open(filename, 'r') as traf:
        data = traf.read()

    traf_data = BeautifulSoup(data, 'xml')

    lane_data = traf_data.find_all(identifier, {'id' : identifier_id})

    desired_data = []

    for i in range(1, len(lane_data)):
        desired_data.append(float(lane_data[i].find("lane").get(parameter)))

    return desired_data

with open("queuedata.xml", 'r') as qd:
    data = qd.read()

queue_data = BeautifulSoup(data, 'xml')

lane_data = queue_data.find_all('lanes')

dsd_0 = []

for i in range(1, len(lane_data)):
    dat = lane_data[i].find("lane", {'id' : '-gneE3_0'})
    if dat:
<<<<<<< HEAD:OSMSims/OSMSimpleMap/xmlxtractor.py
        dsd_0.append(float(dat.get("queueing_length")))
=======
        dsd_0.append(float(dat.get("queueing_time")))
>>>>>>> 4764eca382cad425bf13cfbce8dc462154312d14:DQN_RL/xmlxtractor.py
    else:
        dsd_0.append(0.0)

ticks = [_ for _ in range(1, len(lane_data))]

plt.plot(ticks, dsd_0)
<<<<<<< HEAD:OSMSims/OSMSimpleMap/xmlxtractor.py
plt.title("FC1 N->S QL Data")
plt.xlabel("Timestep")
plt.ylabel("Queueing Data")
plt.savefig('./plots/fc1_ntos_qd.png')
=======
plt.title("FC1 N->S QT Data")
plt.xlabel("Timestep")
plt.ylabel("Queueing Time")
plt.savefig('./plots/fc1_ntos_qt.png')
>>>>>>> 4764eca382cad425bf13cfbce8dc462154312d14:DQN_RL/xmlxtractor.py
plt.close()


dsd_1 = []

for i in range(1, len(lane_data)):
    dat = lane_data[i].find("lane", {'id' : '-gneE1_0'})
    if dat:
<<<<<<< HEAD:OSMSims/OSMSimpleMap/xmlxtractor.py
        dsd_1.append(float(dat.get("queueing_length")))
=======
        dsd_1.append(float(dat.get("queueing_time")))
>>>>>>> 4764eca382cad425bf13cfbce8dc462154312d14:DQN_RL/xmlxtractor.py
    else:
        dsd_1.append(0.0)

ticks = [_ for _ in range(1, len(lane_data))]

plt.plot(ticks, dsd_1)
<<<<<<< HEAD:OSMSims/OSMSimpleMap/xmlxtractor.py
plt.title("FC1 W->E QL Data")
plt.xlabel("Timestep")
plt.ylabel("Queueing Data")
plt.savefig('./plots/fc1_wtoe_qd.png')
=======
plt.title("FC1 W->E QT Data")
plt.xlabel("Timestep")
plt.ylabel("Queueing Time")
plt.savefig('./plots/fc1_wtoe_qt.png')
>>>>>>> 4764eca382cad425bf13cfbce8dc462154312d14:DQN_RL/xmlxtractor.py
plt.close()


dsd_2 = []

for i in range(1, len(lane_data)):
    dat = lane_data[i].find("lane", {'id' : '-gneE5_0'})
    if dat:
<<<<<<< HEAD:OSMSims/OSMSimpleMap/xmlxtractor.py
        dsd_2.append(float(dat.get("queueing_length")))
=======
        dsd_2.append(float(dat.get("queueing_time")))
>>>>>>> 4764eca382cad425bf13cfbce8dc462154312d14:DQN_RL/xmlxtractor.py
    else:
        dsd_2.append(0.0)

ticks = [_ for _ in range(1, len(lane_data))]

plt.plot(ticks, dsd_2)
<<<<<<< HEAD:OSMSims/OSMSimpleMap/xmlxtractor.py
plt.title("FC1 S->N QL Data")
plt.xlabel("Timestep")
plt.ylabel("Queueing Data")
plt.savefig('./plots/fc1_ston_qd.png')
=======
plt.title("FC1 S->N QT Data")
plt.xlabel("Timestep")
plt.ylabel("Queueing Time")
plt.savefig('./plots/fc1_ston_qt.png')
>>>>>>> 4764eca382cad425bf13cfbce8dc462154312d14:DQN_RL/xmlxtractor.py
plt.close()

dsd_3 = []

for i in range(1, len(lane_data)):
    dat = lane_data[i].find("lane", {'id' : 'gneE0_0'})
    if dat:
<<<<<<< HEAD:OSMSims/OSMSimpleMap/xmlxtractor.py
        dsd_3.append(float(dat.get("queueing_length")))
=======
        dsd_3.append(float(dat.get("queueing_time")))
>>>>>>> 4764eca382cad425bf13cfbce8dc462154312d14:DQN_RL/xmlxtractor.py
    else:
        dsd_3.append(0.0)

ticks = [_ for _ in range(1, len(lane_data))]

plt.plot(ticks, dsd_3)
<<<<<<< HEAD:OSMSims/OSMSimpleMap/xmlxtractor.py
plt.title("FC1 E->W QL Data")
plt.xlabel("Timestep")
plt.ylabel("Queueing Data")
plt.savefig('./plots/fc1_etow_qd.png')
=======
plt.title("FC1 E->W QT Data")
plt.xlabel("Timestep")
plt.ylabel("Queueing Time")
plt.savefig('./plots/fc1_etow_qt.png')
>>>>>>> 4764eca382cad425bf13cfbce8dc462154312d14:DQN_RL/xmlxtractor.py
plt.close()