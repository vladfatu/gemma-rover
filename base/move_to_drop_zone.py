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


def get_velocity_from_observation(observation, default_theta):
    front_image = observation["front"]
    cv2.imwrite("front_image.jpg", front_image)

    gray = cv2.cvtColor(front_image, cv2.COLOR_BGR2GRAY)
    # ret, preprocessed_image = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    decoded_objects = decode(gray)
    target_qr = None
    if decoded_objects:
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            if qr_data.strip() == "DEST:Scoop":
                target_qr = obj
                break

    x_vel = 0.0
    y_vel = 0.0
    theta_vel = 0.0

    # If a QR code is detected
    if target_qr:
        print("target_qr:", target_qr)
        # Convert bbox to integer coordinates
        bbox = order_polygon_points(target_qr.polygon)
        print("bbox:", bbox)

        # Draw bounding box
        for i in range(2):
            print("bbox[i]:", bbox[i])
            pt1 = tuple(bbox[i])
            pt2 = tuple(bbox[(i + 1) % len(bbox)])
            cv2.line(front_image, pt1, pt2, (0, 255, 0), 3)

            # Save the new image with bounding box
        cv2.imwrite("output_with_qr_box.jpg", front_image)

        # determine x velocity based on the width of the QR code
        width = target_qr.rect.width
        ideal_width = 210
        print("width:", width)
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
        print("left side:", left_side, "right side:", right_side)
        y_ratio = left_side / right_side
        print("y_ratio:", y_ratio)
        if abs(y_ratio - 1) < 0.025:
            y_vel = 0.0 
        else:
            y_vel = (1 - y_ratio) * 1.1
        print("y_vel:", y_vel)

        # determine rotation based to the position of the QR code relative to the center of the image
        center_x = target_qr.rect.left + (target_qr.rect.width / 2)
        x_delta = abs(center_x - 320)
        print("center_x:", center_x, "x_delta:", x_delta)

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
        print("No QR code detected.")

    default_theta = theta_vel

    return x_vel, y_vel, theta_vel, default_theta


def move_to_drop_zone(default_theta):

    t0 = time.perf_counter()

    observation = robot.get_observation()

    x_vel, y_vel, theta_vel, default_theta = get_velocity_from_observation(observation, default_theta)

    print("theta:", theta_vel)

    base_action = {'x.vel': x_vel, 'y.vel': y_vel, 'theta.vel': theta_vel}

    action = {**SEARCH_ARM_ACTION, **base_action} 

    robot.send_action(action)

    print("time for step:", time.perf_counter() - t0)

    busy_wait(max(1.0 / FPS - (time.perf_counter() - t0), 0.0))

    print("time for step with FPS:", time.perf_counter() - t0)

    return default_theta

default_theta = -5.0
while True:
    default_theta = move_to_drop_zone(default_theta)

# move_to_drop_zone()
