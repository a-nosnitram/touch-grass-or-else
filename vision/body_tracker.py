import mediapipe as mp
import cv2
import vision.contact_logic as contact_logic

# Initialize Mediapipe drawing utilities and holistic model components
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# Start capturing video from the webcams
cap = cv2.VideoCapture(0)


def body_tracker(frame, grass_mask, holistic):
    height, width, _ = frame.shape

    # Convert the BGR image to RGB before processing
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # process the image and get the holistic results
    results = holistic.process(image)

    # convert back to BGR for OpenCV
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    contact_status = contact_logic.check_grass_contact(
        results.pose_landmarks, grass_mask, height, width)

    # draw the landmarks
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_holistic.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(245, 117, 66),
                                   thickness=2, circle_radius=4),
            mp_drawing.DrawingSpec(color=(245, 66, 230),
                                   thickness=2, circle_radius=2)
        )

        # highlight landmarks that are in contact with grass
        for part, in_contact in contact_status.items():
            if in_contact:
                if 'foot' in part:
                    landmark_idx = mp_holistic.PoseLandmark.LEFT_FOOT_INDEX if 'left' in part else mp_holistic.PoseLandmark.RIGHT_FOOT_INDEX
                elif 'hand' in part:
                    landmark_idx = mp_holistic.PoseLandmark.LEFT_INDEX if 'left' in part else mp_holistic.PoseLandmark.RIGHT_INDEX
                elif 'knee' in part:
                    landmark_idx = mp_holistic.PoseLandmark.LEFT_KNEE if 'left' in part else mp_holistic.PoseLandmark.RIGHT_KNEE

                lmrk = results.pose_landmarks.landmark[landmark_idx]
                x = int(lmrk.x * width)
                y = int(lmrk.y * height)

                # circle for contact
                cv2.circle(image, (x, y), 15, (0, 255, 0), -1)

        mp_drawing.draw_landmarks(
            image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        mp_drawing.draw_landmarks(
            image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

    return image, contact_status


if __name__ == "__main__":
    # next we process the video feed frame by frame
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            # process the frame to detect body landmarks
            result, _ = body_tracker(frame, None, holistic)

            # display processed frame
            cv2.imshow('full body detection', result)

            # temporary quit key
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    # release resources
    cap.release()
    cv2.destroyAllWindows()
