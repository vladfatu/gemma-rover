
import time
from lerobot.datasets.utils import hw_to_dataset_features, build_dataset_frame
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.record import record_loop
from lerobot.robots.lekiwi import LeKiwiClient, LeKiwiClientConfig
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import _init_rerun
from lerobot.utils.control_utils import predict_action
from lerobot.utils.utils import get_safe_torch_device

EPISODE_TIME_SEC = 15
TASK_DESCRIPTION = "Pick up the red scoop"

robot_config = LeKiwiClientConfig(remote_ip="192.168.10.19", id="gemma-rover")
robot = LeKiwiClient(robot_config)

print("Loading the policy...")
# policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_scoop_up_to_4")
policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_solar_wipe_up_to_5")
policy.reset()

print("Configuring the dataset features...")
action_features = hw_to_dataset_features(robot.action_features, "action")
obs_features = hw_to_dataset_features(robot.observation_features, "observation")
dataset_features = {**action_features, **obs_features}

print("Connecting to the robot...")
robot.connect()
if not robot.is_connected:
    raise ValueError("Robot is not connected!")

print("Running inference")
start_time = time.time()
while time.time() - start_time < EPISODE_TIME_SEC:
    obs = robot.get_observation()

    observation_frame = build_dataset_frame(dataset_features, obs, prefix="observation")
    # print(f"Observation frame: {observation_frame}")
    action_values = predict_action(
        observation_frame, policy, get_safe_torch_device(policy.config.device), policy.config.use_amp, task=TASK_DESCRIPTION
    )
    action = {key: action_values[i].item() for i, key in enumerate(robot.action_features)}
    robot.send_action(action)

print("Task completed, disconnecting...")
robot.disconnect()
