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

def getTrafData(filename, edge_id, parameter):
    # NOTE: Although './trafficinfo_detailed.xml' has been used, in case of macroscopic parameters, change file to './trafficinfo.xml'
    with open(filename, 'r') as traf:
        data = traf.read()

    traf_data = BeautifulSoup(data, 'xml')

    lane_data = traf_data.find_all("edge", {'id' : edge_id})

    desired_data = []

    for i in range(1, len(lane_data)):
        desired_data.append(float(lane_data[i].find("lane").get(parameter)))

    return desired_data