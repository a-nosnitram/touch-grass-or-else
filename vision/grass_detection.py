import mediapipe as mp
import cv2
import numpy as np

# Initialize Mediapipe drawing utilities and holistic model components
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# Start capturing video from the webcam
cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)


def detect_grass(frame_orig):
    # Note: frame is already flipped in main.py

    # green mask to detect grass
    # BGR to HSV for better color detection
    hsv_frame = cv2.cvtColor(frame_orig, cv2.COLOR_BGR2HSV)

    # only consider lower part of the frame for grass detection
    height, width, _ = hsv_frame.shape
    hsv_frame[0:int(height*0.4), :] = 0

    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])

    # binary mask where grass pixels are white (255)
    grass_mask = cv2.inRange(hsv_frame, lower_green, upper_green)

    # remove noise
    grass_mask = cv2.GaussianBlur(grass_mask, (5, 5), 0)

    # clean up the mask with morphological operations
    kernel = np.ones((5, 5), np.uint8)
    grass_mask = cv2.morphologyEx(grass_mask, cv2.MORPH_CLOSE, kernel)
    grass_mask = cv2.morphologyEx(grass_mask, cv2.MORPH_OPEN, kernel)

    # extract just the grass regions (preserving original colors)
    grass_detected = cv2.bitwise_and(
        frame_orig, frame_orig, mask=grass_mask)

    # highlight grass with semi-transparent overlay
    overlay = frame_orig.copy()
    overlay[grass_mask > 0] = [0, 255, 0]  # Paint detected grass green

    # blend original frame with overlay (30% overlay, 70% original)
    result = cv2.addWeighted(frame_orig, 0.55, overlay, 0.3, 0)

    # draw contours around detected grass regions (plane detection style)
    contours, _ = cv2.findContours(
        grass_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(result, contours, -1, (0, 255, 255), 2)  # Yellow contours

    # remove small areas to reduce noise
    min_contour_area = 500  # Minimum area threshold
    for contour in contours:
        if cv2.contourArea(contour) < min_contour_area:
            cv2.drawContours(result, [contour], -1, (0, 255, 255), -1)
    return result, grass_mask


if __name__ == "__main__":
    # Process the video feed frame by frame
    with mp_holistic.Holistic(min_detection_confidence=0.7, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            ret, frame_orig = cap.read()

            if not ret:
                print("Ignoring empty camera frame.")
                break

            # Detect grass in the frame
            result, grass_mask = detect_grass(frame_orig)

            # Show results
            # cv2.imshow('Original', frame_orig)
            # cv2.imshow('Grass Mask', grass_mask)
            cv2.imshow('Grass Detection (AR Style)', result)

            # Quit on 'q' key
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
