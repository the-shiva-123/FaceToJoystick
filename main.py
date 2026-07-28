import cv2
import os
import sys
import math
import vgamepad as vg
import FaceDetection
from FaceDetection import detect_face, previous_faces
import JoystickControl
import numpy as np
from helpers import process_frame
import variables

# Initialize gamepad
gamepad = vg.VX360Gamepad()


def calculate_head_roll(points):
    """Calculates the head tilt angle (roll) in degrees from tracked points."""
    if points is None or len(points) < 2:
        return 0.0

    # Reshape points array to (N, 2)
    pts = points.reshape(-1, 2)
    center_x = np.mean(pts[:, 0])

    # Split tracking points into left and right clusters relative to face center
    left_pts = pts[pts[:, 0] < center_x]
    right_pts = pts[pts[:, 0] >= center_x]

    if len(left_pts) == 0 or len(right_pts) == 0:
        return 0.0

    # Find center mass of left and right clusters
    left_center = np.mean(left_pts, axis=0)
    right_center = np.mean(right_pts, axis=0)

    # Calculate angle in degrees
    dx = right_center[0] - left_center[0]
    dy = right_center[1] - left_center[1]

    return math.degrees(math.atan2(dy, dx))


def main():
    global initial_face_x, initial_face_y
    cap = cv2.VideoCapture(0)

    # Initialize trackbars
    cv2.namedWindow("FaceToJoystick")
    cv2.createTrackbar("Deadzone X", "FaceToJoystick",
                       variables.deadzone_threshold_x, 100, variables.on_change_deadzone_x)
    cv2.createTrackbar("Deadzone Y", "FaceToJoystick",
                       variables.deadzone_threshold_y, 100, variables.on_change_deadzone_y)
    cv2.createTrackbar("Sensitivity X", "FaceToJoystick",
                       variables.sensitivity_x, 20, variables.on_change_sensitivity_x)
    cv2.createTrackbar("Sensitivity Y", "FaceToJoystick",
                       variables.sensitivity_y, 20, variables.on_change_sensitivity_y)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Process frame
        frame = process_frame(frame)

        # Calculate Head Roll angle using tracked points from FaceDetection module
        roll_angle = calculate_head_roll(FaceDetection.prev_points)

        # Trigger LB/RB buttons based on head tilt angle
        if roll_angle > 10:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        elif roll_angle < -10:
            gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
        else:
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
            gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)

        gamepad.update()

        # Display frame
        cv2.imshow("FaceToJoystick", frame)
        cv2.setWindowProperty(
            "FaceToJoystick", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
        )

        # Handle key events
        key = cv2.waitKey(1) & 0xFF
        if key == ord("r"):
            variables.initial_face_x = None
            variables.initial_face_y = None
        elif key == ord("q"):
            break
        elif key == ord("s"):
            os.execv(sys.executable, ['python'] + sys.argv)
        elif key == ord("i"):
            variables.rotate_camera = True

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()