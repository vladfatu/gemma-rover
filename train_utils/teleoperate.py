import time

from lerobot.robots.lekiwi import LeKiwiClient, LeKiwiClientConfig
from lerobot.teleoperators.keyboard.teleop_keyboard import KeyboardTeleop, KeyboardTeleopConfig
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig
from lerobot.utils.robot_utils import busy_wait
from lerobot.utils.visualization_utils import _init_rerun, log_rerun_data

SEARCH_ARM_ACTION = {'arm_shoulder_pan.pos': -5.0, 'arm_shoulder_lift.pos': -98.92428630533719, 'arm_elbow_flex.pos': 99.27895448400182, 'arm_wrist_flex.pos': 19.973137973137966, 'arm_wrist_roll.pos': -0.31746031746031633, 'arm_gripper.pos': 0.867244829886591}

FPS = 30

# Create the robot and teleoperator configurations
robot_config = LeKiwiClientConfig(remote_ip="192.168.10.19", id="gemma-rover")
teleop_arm_config = SO101LeaderConfig(port="/dev/tty.usbmodem5A460849101", id="leader_101")
keyboard_config = KeyboardTeleopConfig(id="my_laptop_keyboard")

robot = LeKiwiClient(robot_config)
leader_arm = SO101Leader(teleop_arm_config)
keyboard = KeyboardTeleop(keyboard_config)

# To connect you already should have this script running on LeKiwi: `python -m lerobot.robots.lekiwi.lekiwi_host --robot.id=my_awesome_kiwi`
robot.connect()
keyboard.connect()

try:
    leader_arm.connect()
except ConnectionError as e:
    print(f"Failed to connect leader arm: Running without leader arm. Error: {e}")

_init_rerun(session_name="lekiwi_teleop")

# if not robot.is_connected or not leader_arm.is_connected or not keyboard.is_connected:
#     raise ValueError("Robot, leader arm or keyboard is not connected!")

while True:
    t0 = time.perf_counter()

    observation = robot.get_observation()

    if leader_arm.is_connected:
        arm_action = leader_arm.get_action()
        arm_action = {f"arm_{k}": v for k, v in arm_action.items()}
    else:
        arm_action = SEARCH_ARM_ACTION


    keyboard_keys = keyboard.get_action()
    base_action = robot._from_keyboard_to_base_action(keyboard_keys)

    log_rerun_data(observation, {**arm_action, **base_action})

    action = {**arm_action, **base_action} if len(base_action) > 0 else arm_action

    robot.send_action(action)

    busy_wait(max(1.0 / FPS - (time.perf_counter() - t0), 0.0))
