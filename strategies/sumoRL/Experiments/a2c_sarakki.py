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
import time


if __name__ == '__main__':

    #write_route_file('nets/2way-single-intersection/single-intersection-gen.rou.xml', 400000, 100000)

    # multiprocess environment
    n_cpu = 1
    env = SubprocVecEnv([lambda: SumoEnvironment(net_file='Sarakki_network_weib/osm.net.xml',
                                        route_file='Sarakki_network_weib/network/train/ew_loaded.rou.xml',
                                        out_csv_name='Sarakki_outputs/Train_weib_ewload_green10/train',
                                        single_agent=True,
                                        use_gui=False,
                                        num_seconds=5500,
                                        min_green=10,
                                        delta_time=10,
                                        yellow_time=2,
                                        max_depart_delay=0) for _ in range(n_cpu)])

    model = A2C(MlpPolicy, env, verbose=1, learning_rate=0.001, lr_schedule='constant')
    start = time.time()
    model.learn(total_timesteps=15000)
    end = time.time()
    model.save("Sarakki_models/a2c_ncpu=1_ewload_green10_15k")
    print('Training has Ended!')
    print('TIME TAKEN IS:', end-start)

    # del model

    # print('Testing has begun!')

    # model = A2C.load("models/a2csimpleMapVidali", env = env, policy = MlpPolicy)
    # obs = env.reset()
    # for i in range(5400):
    #     action, _states = model.predict(obs)
    #     obs, rewards, dones, info = env.step(action)
    #     #print(i, rewards, dones, info)
