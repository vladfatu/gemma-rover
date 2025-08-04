

def move_robot_to_qr_code(robot, qr_code_description, cancel_event, inside_base):
    if robot:
        robot.move_to(qr_code_description)
    else:
        print("Simulating robot movement to QR code location:", qr_code_description)
