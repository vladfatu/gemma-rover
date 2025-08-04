import time
import numpy as np
import cv2
from pyzbar.pyzbar import decode
from lerobot.utils.robot_utils import busy_wait

FPS = 20
DEFAULT_SEARCH_ARM_ACTION = {'arm_shoulder_pan.pos': -5.0, 'arm_shoulder_lift.pos': -98.0, 'arm_elbow_flex.pos': 99.0, 'arm_wrist_flex.pos': 19.0, 'arm_wrist_roll.pos': -0.3, 'arm_gripper.pos': 0.9}
NAVIGATION_TIME_SEC = 20

def get_distance(point1, point2):
    return ((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2) ** 0.5

def order_polygon_points(pts):
    # Convert to array
    pts = np.array(pts, dtype="int")

    # Calculate sum and difference
    s = pts.sum(axis=1)          # top-left will have smallest sum, bottom-right largest
    diff = np.diff(pts, axis=1)  # top-right will have smallest diff, bottom-left largest

    ordered = np.zeros((4, 2), dtype="int")
    ordered[0] = pts[np.argmin(s)]       # Top-left
    ordered[2] = pts[np.argmax(s)]       # Bottom-right
    ordered[1] = pts[np.argmin(diff)]    # Top-right
    ordered[3] = pts[np.argmax(diff)]    # Bottom-left

    return ordered

def get_velocity_from_observation(observation, default_theta, target_qr_message):
    front_image = observation["front"]

    gray = cv2.cvtColor(front_image, cv2.COLOR_BGR2GRAY)
    decoded_objects = decode(gray)
    target_qr = None
    if decoded_objects:
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            if qr_data.strip() == target_qr_message:
                target_qr = obj
                break

    x_vel = 0.0
    y_vel = 0.0
    theta_vel = 0.0

    # If a QR code is detected
    if target_qr:
        # Convert bbox to integer coordinates
        bbox = order_polygon_points(target_qr.polygon)

        # Draw bounding box
        for i in range(2):
            pt1 = tuple(bbox[i])
            pt2 = tuple(bbox[(i + 1) % len(bbox)])
            cv2.line(front_image, pt1, pt2, (0, 255, 0), 3)

        # determine x velocity based on the width of the QR code
        width = target_qr.rect.width
        ideal_width = 210
        if width > ideal_width:
            x_vel = 0.0
        else:
            if width < ideal_width:
                x_vel = 0.05
            else:
                x_vel = -0.05

        # determine y velocity base on the ratio between the left and right side of the QR code
        left_side = get_distance(bbox[0], bbox[3])
        right_side = get_distance(bbox[1], bbox[2])
        y_ratio = left_side / right_side
        if abs(y_ratio - 1) < 0.025:
            y_vel = 0.0 
        else:
            y_vel = (1 - y_ratio) * 1.1

        # determine rotation based to the position of the QR code relative to the center of the image
        center_x = target_qr.rect.left + (target_qr.rect.width / 2)
        x_delta = abs(center_x - 320)

        if x_delta > 25:
            if center_x < 320:
                theta_vel = 3.0
            elif center_x > 320:    
                theta_vel = -3.0
        else:
            theta_vel = 0.0

    else:
        x_vel = 0.0
        y_vel = 0.0
        theta_vel = default_theta

    default_theta = theta_vel

    return x_vel, y_vel, theta_vel, default_theta

def move_incrementally(robot, default_theta, target_qr_message):
    t0 = time.perf_counter()

    observation = robot.get_observation()
    x_vel, y_vel, theta_vel, default_theta = get_velocity_from_observation(observation, default_theta, target_qr_message)
    base_action = {'x.vel': x_vel, 'y.vel': y_vel, 'theta.vel': theta_vel}

    action = {**DEFAULT_SEARCH_ARM_ACTION, **base_action}
    robot.send_action(action)

    busy_wait(max(1.0 / FPS - (time.perf_counter() - t0), 0.0))
    return default_theta

def do_a_180(robot):
    print("Doing a 180")
    start_time = time.time()
    while time.time() - start_time < 20:
        base_action = {'x.vel': 0.0, 'y.vel': 0.0, 'theta.vel': 10.0}
        action = {**DEFAULT_SEARCH_ARM_ACTION, **base_action}
        robot.send_action(action)

def move_forward(robot, seconds):
    start_time = time.time()
    while time.time() - start_time < seconds:
        base_action = {'x.vel': 0.1, 'y.vel': 0.0, 'theta.vel': 0.0}
        action = {**DEFAULT_SEARCH_ARM_ACTION, **base_action}
        robot.send_action(action)

def move_robot_to_qr_code(robot, qr_code_description, cancel_event, inside_base):

    # If the rover is inside the base, move out of the base first
    if inside_base:
        move_forward(robot, 5.0)

    default_theta = -5.0
    start_time = time.time()
    while not cancel_event.is_set() and time.time() - start_time < NAVIGATION_TIME_SEC :
        default_theta = move_incrementally(robot, default_theta, qr_code_description)

    # If the destination QR code is "DEST:HomeBase", after getting in front of the base, move inside and do a 180
    if qr_code_description == "DEST:HomeBase":
        move_forward(robot, 5.0)
        do_a_180(robot)

