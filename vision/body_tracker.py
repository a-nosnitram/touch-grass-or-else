import mediapipe as mp
import cv2

# Initialize Mediapipe drawing utilities and holistic model components
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# Start capturing video from the webcam
cap = cv2.VideoCapture(0)


def body_tracker(frame):
    # Convert the BGR image to RGB before processing
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # process the image and get the holistic results
    results = holistic.process(image)

    # convert back to BGR for OpenCV
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # draw the landmarks
    # face
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS, mp_drawing.DrawingSpec(color=(
        80, 110, 10), thickness=1, circle_radius=1), mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1))

    # right hand
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, mp_drawing.DrawingSpec(color=(
        80, 110, 10), thickness=1, circle_radius=1), mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1))

    # left hand
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, mp_drawing.DrawingSpec(color=(
        80, 110, 10), thickness=1, circle_radius=1), mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1))

    # pose
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, mp_drawing.DrawingSpec(color=(
        245, 117, 66), thickness=2, circle_radius=4), mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

    return image


# next we process the video feed frame by frame
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        # process the frame to detect body landmarks
        result = body_tracker(frame)

        # display processed frame
        cv2.imshow('full body detection', result)

        # temporary quit key
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

# release resources
cap.release()
cv2.destroyAllWindows()
