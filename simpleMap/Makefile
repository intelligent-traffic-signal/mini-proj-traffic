SIM_TIME=50

PASS_PARAMS=-e $(SIM_TIME) -l -p 1 --vehicle-class passenger --trip-attributes="color=\"255,255,255\""
BUS_PARAMS=-e $(SIM_TIME) -l -p 30 --vehicle-class bus --trip-attributes="accel=\"20.8\""
TRUCK_PARAMS=-e $(SIM_TIME) -l -p 15 --vehicle-class truck --trip-attributes="color=\"179,253,183\""
DELIVERY_PARAMS=-e $(SIM_TIME) -l -p 30 --vehicle-class delivery --trip-attributes="color=\"115,211,230\""

# REPLACE WITH MAP NAME
MAP_NAME=simpleMap

all: osm trips

trips:
	# Generate random trips for all vehicle types
	python randomTrips.py -n $(MAP_NAME).net.xml -r passenger_routes.rou.xml -o passenger_trips.xml $(PASS_PARAMS)
	python randomTrips.py -n $(MAP_NAME).net.xml -r bus_routes.rou.xml -o bus_trips.xml $(BUS_PARAMS)
	python randomTrips.py -n $(MAP_NAME).net.xml -r truck_routes.rou.xml -o truck_trips.xml $(TRUCK_PARAMS)
	python randomTrips.py -n $(MAP_NAME).net.xml -r delivery_routes.rou.xml -o delivery_trips.xml $(DELIVERY_PARAMS)

	# Unique IDs for vehicles
	sed -i "" "s/vehicle id=\"/vehicle id=\"passenger/g" passenger_routes.rou.xml
	sed -i "" "s/vehicle id=\"/vehicle id=\"bus/g" bus_routes.rou.xml
	sed -i "" "s/vehicle id=\"/vehicle id=\"truck/g" truck_routes.rou.xml
	sed -i "" "s/vehicle id=\"/vehicle id=\"delivery/g" delivery_routes.rou.xml

osm:
	netconvert --osm-files $(MAP_NAME).osm --lefthand -o $(MAP_NAME).net.xml
	# Polygon
	polyconvert --osm-files $(MAP_NAME).osm --net-file $(MAP_NAME).net.xml --type-file $(MAP_NAME).typ.xml -o $(MAP_NAME).poly.xml

sim:
	sumo-gui $(MAP_NAME).sumocfg

rr:
	python trafficlights.py

clean:
	rm -f *.rou.xml *.rou.alt.xml *trips.xml
	rm -f $(MAP_NAME).poly.xml