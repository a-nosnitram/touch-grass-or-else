import mediapipe as mp
import cv2

# Initialize Mediapipe drawing utilities and holistic model components
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic  # used for landmark visualisation

# Start capturing video from the webcam
cap = cv2.VideoCapture(1)
