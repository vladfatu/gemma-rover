import time

from lerobot.robots.lekiwi import LeKiwiClient, LeKiwiClientConfig
from lerobot.utils.robot_utils import busy_wait
import cv2
from pyzbar.pyzbar import decode
import numpy as np

SEARCH_ARM_ACTION = {'arm_shoulder_pan.pos': -5.0, 'arm_shoulder_lift.pos': -98.92428630533719, 'arm_elbow_flex.pos': 99.27895448400182, 'arm_wrist_flex.pos': 19.973137973137966, 'arm_wrist_roll.pos': -0.31746031746031633, 'arm_gripper.pos': 0.867244829886591}

FPS = 20

robot_config = LeKiwiClientConfig(remote_ip="192.168.10.19", id="gemma-rover")

robot = LeKiwiClient(robot_config)

robot.connect()



def move_out_of_base():
    print("Moving out of base")
    start_time = time.time()
    while time.time() - start_time < 5:
        base_action = {'x.vel': 0.15, 'y.vel': 0.0, 'theta.vel': 0.0}
        action = {**SEARCH_ARM_ACTION, **base_action}
        robot.send_action(action)

    # robot.send_action({'x.vel': 0.0, 'y.vel': 0.0, 'theta.vel': 0.0})
    print("Moved out of base")

def do_a_180():
    print("Doing a 180")
    start_time = time.time()
    while time.time() - start_time < 20:
        base_action = {'x.vel': 0.0, 'y.vel': 0.0, 'theta.vel': 10.0}
        action = {**SEARCH_ARM_ACTION, **base_action}
        robot.send_action(action)

    # robot.send_action({'x.vel': 0.0, 'y.vel': 0.0, 'theta.vel': 0.0})
    print("Moved out of base")


def move_from_cloth_to_solar_panel():
    print("Moving from cloth to solar panel")
    start_time = time.time()
    while time.time() - start_time < 5:
        base_action = {'x.vel': 0.0, 'y.vel': 0.05, 'theta.vel': 0.0}
        action = {**SEARCH_ARM_ACTION, **base_action}
        robot.send_action(action)

    # robot.send_action({'x.vel': 0.0, 'y.vel': 0.0, 'theta.vel': 0.0})
    print("Moved out of base")

# move_out_of_base()
# do_a_180()
# move_out_of_base()
move_from_cloth_to_solar_panel()