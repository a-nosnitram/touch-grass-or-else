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


def check_grass_contact(body_landmarks, grass_mask):
