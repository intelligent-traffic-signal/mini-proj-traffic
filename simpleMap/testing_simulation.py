import traci
import numpy as np
from math import sqrt
import timeit

# phase codes based on environment.net.xml
PHASE_S_GREEN = 0   # action 0 code 00
PHASE_S_YELLOW = 1
PHASE_E_GREEN = 2   # action 1 code 01
PHASE_E_YELLOW = 3
PHASE_N_GREEN = 4   # action 2 code 10
PHASE_N_YELLOW = 5
PHASE_W_GREEN = 6   # action 3 code 11
PHASE_W_YELLOW = 7

ROAD_LEN = 242.8

# Cumulative cell positions
CELL_1 = 7
CELL_2 = 14
CELL_3 = 21
CELL_4 = 28
CELL_5 = 40
CELL_6 = 60
CELL_7 = 100
CELL_8 = 160
CELL_9 = ROAD_LEN

class Simulation:
    def __init__(self, Model, TrafficGen, sumo_cmd, max_steps, green_duration, yellow_duration, num_states, num_actions):
        self._Model = Model
        self._TrafficGen = TrafficGen
        self._step = 0
        self._sumo_cmd = sumo_cmd
        self._max_steps = max_steps
        self._green_duration = green_duration
        self._yellow_duration = yellow_duration
        self._num_states = num_states
        self._num_actions = num_actions
        self._reward_episode = []
        self._queue_length_episode = []

    def _reward(self, old_total_wait, current_total_wait):
        return 0.9*old_total_wait - current_total_wait

    def run(self, episode):
        """
        Runs the testing simulation
        """
        start_time = timeit.default_timer()

        # first, generate the route file for this simulation and set up sumo
        self._TrafficGen.generate_routefile(seed=episode)
        traci.start(self._sumo_cmd)
        print("Simulating...")

        # inits
        self._step = 0
        self._waiting_times = {}
        old_total_wait = 0
        old_action = -1 # dummy init

        while self._step < self._max_steps:

            # get current state of the intersection
            current_state = self._get_state()

            # print(current_state)

            # calculate reward of previous action: (change in cumulative waiting time between actions)
            # waiting time = seconds waited by a car since the spawn in the environment, cumulated for every car in incoming lanes
            current_total_wait = self._collect_waiting_times()
            
            reward = self._reward(old_total_wait, current_total_wait)

            # choose the light phase to activate, based on the current state of the intersection
            action = self._choose_action(current_state)

            # if the chosen phase is different from the last phase, activate the yellow phase
            if self._step != 0 and old_action != action:
                self._set_yellow_phase(old_action)
                self._simulate(self._yellow_duration)

            # execute the phase selected before
            self._set_green_phase(action)
            self._simulate(self._green_duration)

            # saving variables for later & accumulate reward
            old_action = action
            old_total_wait = current_total_wait

            self._reward_episode.append(reward)

        #print("Total reward:", np.sum(self._reward_episode))
        traci.close()
        simulation_time = round(timeit.default_timer() - start_time, 1)

        return simulation_time


    def _simulate(self, steps_todo):
        """
        Proceed with the simulation in sumo
        """
        if (self._step + steps_todo) >= self._max_steps:  # do not do more steps than the maximum allowed number of steps
            steps_todo = self._max_steps - self._step

        while steps_todo > 0:
            traci.simulationStep()  # simulate 1 step in sumo
            self._step += 1 # update the step counter
            steps_todo -= 1
            queue_length = self._get_queue_length() 
            self._queue_length_episode.append(queue_length)


    def _collect_waiting_times(self):
        """
        Retrieve the waiting time of every car in the incoming roads
        """
        incoming_roads = ["E2T", "N2T", "W2T", "S2T"]
        car_list = traci.vehicle.getIDList()
        for car_id in car_list:
            wait_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
            road_id = traci.vehicle.getRoadID(car_id)  # get the road id where the car is located
            if road_id in incoming_roads:  # consider only the waiting times of cars in incoming roads
                # TODO:
                self._waiting_times[car_id] = wait_time*wait_time
            else:   # not in incoming road
                if car_id in self._waiting_times: # a car that was tracked has cleared the intersection
                    del self._waiting_times[car_id] 
        total_waiting_time = sum([sqrt(i) for i in self._waiting_times.values()])
        return total_waiting_time


    def _choose_action(self, state):
        """
        Pick the best action known based on the current state of the env
        """
        return np.argmax(self._Model.predict_one(state))


    def _set_yellow_phase(self, old_action):
        """
        Activate the correct yellow light combination in sumo
        """
        yellow_phase_code = old_action * 2 + 1 # obtain the yellow phase code, based on the old action (ref on environment.net.xml)
        traci.trafficlight.setPhase("t0", yellow_phase_code)


    def _set_green_phase(self, action_number):
        """
        Activate the correct green light combination in sumo
        """

        if action_number == 0:
            traci.trafficlight.setPhase("t0", PHASE_S_GREEN)
        elif action_number == 1:
            traci.trafficlight.setPhase("t0", PHASE_E_GREEN)
        elif action_number == 2:
            traci.trafficlight.setPhase("t0", PHASE_N_GREEN)
        elif action_number == 3:
            traci.trafficlight.setPhase("t0", PHASE_W_GREEN)


    def _get_queue_length(self):
        """
        Retrieve the number of cars with speed = 0 in every incoming lane
        """
        halt_N = traci.edge.getLastStepHaltingNumber("N2T")
        halt_S = traci.edge.getLastStepHaltingNumber("S2T")
        halt_E = traci.edge.getLastStepHaltingNumber("E2T")
        halt_W = traci.edge.getLastStepHaltingNumber("W2T")
        queue_length = halt_N + halt_S + halt_E + halt_W
        return queue_length


    def _get_state(self):
        """
        Retrieve the state of the intersection from sumo, in the form of cell occupancy
        """
        state = np.zeros(self._num_states)
        car_list = traci.vehicle.getIDList()

        for car_id in car_list:
            lane_pos = traci.vehicle.getLanePosition(car_id)
            lane_id = traci.vehicle.getLaneID(car_id)
            lane_pos = ROAD_LEN - lane_pos  # inversion of lane pos, so if the car is close to the traffic light -> lane_pos = 0 --- ROAD_LEN = max len of a road

            # distance in meters from the traffic light -> mapping into cells
            if lane_pos < CELL_1:
                lane_cell = 0
            elif lane_pos < CELL_2:
                lane_cell = 1
            elif lane_pos < CELL_3:
                lane_cell = 2
            elif lane_pos < CELL_4:
                lane_cell = 3
            elif lane_pos < CELL_5:
                lane_cell = 4
            elif lane_pos < CELL_6:
                lane_cell = 5
            elif lane_pos < CELL_7:
                lane_cell = 6
            elif lane_pos < CELL_8:
                lane_cell = 7
            elif lane_pos < CELL_9:
                lane_cell = 8

            # finding the lane (edge) where the car is located 
            if lane_id == "S2T_0":
                lane_group = 0
            elif lane_id == "E2T_0":
                lane_group = 1
            elif lane_id == "N2T_0":
                lane_group = 2
            elif lane_id == "W2T_0":
                lane_group = 3
            else:
                lane_group = -1

            if lane_group >= 0 and lane_group < 4:
                car_position = lane_group * 9 + lane_cell  # composition of the two postion ID to create a number in interval 0-35
                valid_car = True
            else:
                valid_car = False  # flag for not detecting cars crossing the intersection or driving away from it

            if valid_car:
                state[car_position] = 1  # write the position of the car car_id in the state array in the form of "cell occupied"

        return state


    @property
    def queue_length_episode(self):
        return self._queue_length_episode


    @property
    def reward_episode(self):
        return self._reward_episode



