import os
import sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")
from sumo_rl import SumoEnvironment
from sumo_rl.util.gen_route import write_route_file
import traci

from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines import A2C


if __name__ == '__main__':

    #write_route_file('nets/2way-single-intersection/single-intersection-gen.rou.xml', 400000, 100000)

    # multiprocess environment
    n_cpu = 1
    env = SubprocVecEnv([lambda: SumoEnvironment(net_file='Sarakki_network_weib/osm.net.xml',
                                        route_file='Sarakki_network_weib/network/test/ns_loaded.rou.xml',
                                        out_csv_name='Sarakki_outputs/Test_weib/ncpu=1_15k/test_nsload_green10',
                                        single_agent=True,
                                        use_gui=True,
                                        num_seconds=5500,
                                        min_green=10,
                                        delta_time=10,
                                        yellow_time=2,
                                        max_depart_delay=0) for _ in range(n_cpu)])


    model = A2C.load("Sarakki_models/a2c_ncpu=1_nsload_green10_15k", env = env, policy = MlpPolicy)
    obs = env.reset()
    for i in range(700):
        action, _states = model.predict(obs)
        obs, rewards, dones, info = env.step(action)
        #print(i, rewards, dones, info)
