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
    train_env = SubprocVecEnv([lambda: SumoEnvironment(net_file='network/simpleMap.net.xml',
                                        route_file='network/train_routes.rou.xml',
                                        out_csv_name='outputs/simpleMap_a2c/training2nd',
                                        single_agent=True,
                                        use_gui=False,
                                        num_seconds=1000,
                                        min_green=5,
                                        max_depart_delay=0) for _ in range(n_cpu)])

    test_env = SubprocVecEnv([lambda: SumoEnvironment(net_file='network/simpleMap.net.xml',
                                        route_file='network/test_routes.rou.xml',
                                        out_csv_name='outputs/simpleMap_a2c/testing2nd',
                                        single_agent=True,
                                        use_gui=False,
                                        num_seconds=5400,
                                        min_green=5,
                                        max_depart_delay=0) for _ in range(n_cpu)])

    model = A2C(MlpPolicy, train_env, verbose=1, learning_rate=0.001, lr_schedule='constant')
    model.learn(total_timesteps=1000)
    model.save("a2csimpleMap")

    del model

    model = A2C.load("a2csimpleMap")
    obs = test_env.reset()
    for i in range(5401):
        action, _states = model.predict(obs)
        obs, rewards, dones, info = test_env.step(action)
        print(i, rewards, dones, info)
