
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

EPISODE_TIME_SEC = 10
TASK_DESCRIPTION = "Drop the dirt sample in the drop zone"

robot_config = LeKiwiClientConfig(remote_ip="192.168.10.19", id="gemma-rover")
robot = LeKiwiClient(robot_config)

print("Loading the policy...")
policy = ACTPolicy.from_pretrained("vladfatu/gemma_rover_drop_dirt_up_to_5")
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

SEARCH_ARM_ACTION = {'arm_shoulder_pan.pos': -5.0, 'arm_shoulder_lift.pos': -98.92428630533719, 'arm_elbow_flex.pos': 99.27895448400182, 'arm_wrist_flex.pos': 19.973137973137966, 'arm_wrist_roll.pos': -0.31746031746031633, 'arm_gripper.pos': 0.867244829886591}
base_action = {'x.vel': 0.0, 'y.vel': 0.0, 'theta.vel': 0.0}
action = {**SEARCH_ARM_ACTION, **base_action}

robot.send_action(action)
time.sleep(2)

print("Task completed, disconnecting...")
robot.disconnect()
