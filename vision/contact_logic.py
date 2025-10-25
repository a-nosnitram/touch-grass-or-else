# detect contact between body parts and the grass in the video feed
import mediapipe as mp
import cv2
import numpy as np

import vision.grass_detection as grass_detection
import vision.body_tracker as body_tracker

# Initialize Mediapipe drawing utilities and holistic model components
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# Start capturing video from the webcam
cap = cv2.VideoCapture(0)


def check_grass_contact(pose_landmarks, grass_mask, frame_height, frame_width):
    if not pose_landmarks:
        return {}

    contact_status = {
        "left_foot": False,
        "right_foot": False,
        "left_hand": False,
        "right_hand": False,
        "right_knee": False,
        "left_knee": False
    }

    # define which mediapipe landmarks cprrespond to body parts
    body_parts = {
        'left_foot': mp_holistic.PoseLandmark.LEFT_FOOT_INDEX,
        'right_foot': mp_holistic.PoseLandmark.RIGHT_FOOT_INDEX,
        'left_hand': mp_holistic.PoseLandmark.LEFT_INDEX,
        'right_hand': mp_holistic.PoseLandmark.RIGHT_INDEX,
        'left_knee': mp_holistic.PoseLandmark.LEFT_KNEE,
        'right_knee': mp_holistic.PoseLandmark.RIGHT_KNEE
    }

    # check for the grass-to-body contact
    for part, landmark_idx in body_parts.items():
        lmrk = pose_landmarks.landmark[landmark_idx]

        # convert normalised coordinates to pixel coordinates
        x = int(lmrk.x * frame_width)
        y = int(lmrk.y * frame_height)

        # check that coordinates are within the frame
        if 0 <= x < frame_width and 0 <= y < frame_height:
            # check if pixel is on grass
            radius = 10
            x_min = max(0, x - radius)
            x_max = min(frame_width, x + radius)
            y_min = max(0, y - radius)
            y_max = min(frame_height, y + radius)

            # if any pixel in the region is grass, count this as contact
            region = grass_mask[y_min:y_max, x_min:x_max]
            if np.any(region > 0):
                contact_status[part] = True
                print(f"Contact detected: {part}")

    return contact_status
