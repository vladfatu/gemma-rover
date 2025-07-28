import time
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.robots import robot
from lerobot.robots.lekiwi import LeKiwiClient, LeKiwiClientConfig
from lerobot.utils.control_utils import predict_action
from lerobot.utils.utils import get_safe_torch_device
from lerobot.datasets.utils import hw_to_dataset_features, build_dataset_frame


class LeRobotTaskHandler:
    def __init__(self, robot):
        self.robot = robot
        print("Loading policies...")
        self.scoop_up_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_scoop_up_to_4")
        self.scoop_put_back_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_scoop_drop_up_to_7")
        self.cloth_pick_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_cloth_up_to_5")
        self.cloth_put_back_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_cloth_drop_up_to_3")
        self.dirt_sample_pick_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_dig_up_to_5")
        self.dirt_sample_drop_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_drop_dirt_up_to_5")
        self.solar_wipe_policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_solar_wipe_up_to_5")

        print("Connecting to the robot...")
        robot_config = LeKiwiClientConfig(remote_ip="192.168.10.19", id="gemma-rover")
        self.robot = LeKiwiClient(robot_config)
        self.robot.connect()
        if not self.robot.is_connected:
            raise ValueError("Robot is not connected!")
        
        print("Configuring the dataset features...")
        action_features = hw_to_dataset_features(self.robot.action_features, "action")
        obs_features = hw_to_dataset_features(self.robot.observation_features, "observation")
        self.dataset_features = {**action_features, **obs_features}


    def run_policy_task(self, policy, task_description, episode_time_sec=15):
        # TODO check if policy needs to be reset
        # policy.reset()
        start_time = time.time()
        while time.time() - start_time < episode_time_sec:
            obs = self.robot.get_observation()

            observation_frame = build_dataset_frame(self.dataset_features, obs, prefix="observation")
            
            action_values = predict_action(
                observation_frame, policy, get_safe_torch_device(policy.config.device), policy.config.use_amp, task=task_description
            )
            action = {key: action_values[i].item() for i, key in enumerate(self.robot.action_features)}
            self.robot.send_action(action)

    def pick_scoop(self):
        self.run_policy_task(self.scoop_up_policy, "Pick up the red scoop", episode_time_sec=15)


    def put_scoop_back(self):
        self.run_policy_task(self.scoop_put_back_policy, "Put the red scoop down", episode_time_sec=15)


    def pick_cloth(self):
        self.run_policy_task(self.cloth_pick_policy, "Pick up the cloth", episode_time_sec=15)


    def put_cloth_back(self):
        self.run_policy_task(self.cloth_put_back_policy, "Put the cloth down", episode_time_sec=15)


    def pick_dirt_sample(self):
        self.run_policy_task(self.dirt_sample_pick_policy, "Use the scoop to pick up dirt samples", episode_time_sec=15)


    def drop_dirt_sample(self):
        self.run_policy_task(self.dirt_sample_drop_policy, "Put the dirt in the drop zone", episode_time_sec=15)
        

    def wipe_solar_panel(self):
        self.run_policy_task(self.solar_wipe_policy, "Wipe the solar panel with the cloth", episode_time_sec=15)