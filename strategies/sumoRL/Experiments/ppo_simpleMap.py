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
from stable_baselines import PPO2


if __name__ == '__main__':

    #write_route_file('nets/2way-single-intersection/single-intersection-gen.rou.xml', 400000, 100000)

    # multiprocess environment
    n_cpu = 4
    env = SubprocVecEnv([lambda: SumoEnvironment(net_file='network/simpleMap.net.xml',
                                        route_file='network/final_routes.rou.xml',
                                        out_csv_name='outputs/ppo2_final_ncpu=4/train',
                                        single_agent=True,
                                        use_gui=False,
                                        num_seconds=5400,
                                        min_green=5,
                                        max_depart_delay=0) for _ in range(n_cpu)])

    model = PPO2(MlpPolicy, env, verbose=1, learning_rate=0.001)
    model.learn(total_timesteps=5400)
    model.save("pposimpleMap")
    print('Training has Ended!')

    del model

    print('Testing has begun!')

    model = PPO2.load("pposimpleMap", env = env, policy = MlpPolicy)
    obs = env.reset()
    for i in range(5400):
        action, _states = model.predict(obs)
        obs, rewards, dones, info = env.step(action)
        #print(i, rewards, dones, info)
