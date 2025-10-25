import vision.body_tracker as body_tracker
import vision.grass_detection as grass_detection
import mediapipe as mp
import cv2


# Initialize Mediapipe drawing utilities and holistic model components
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# Start capturing video from the webcams
cap = cv2.VideoCapture(0)

# next we process the video feed frame by frame
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        ret, frame_orig = cap.read()

        if not ret:
            break

        # flip frame
        frame = cv2.flip(frame_orig, 1)

        # get the grass mask (but don't use the green overlay yet)
        grass_result, grass_mask = grass_detection.detect_grass(frame)

        # process body tracking on ORIGINAL frame (not grass overlay)
        body_result, contact_status = body_tracker.body_tracker(
            frame, grass_mask, holistic)

        # Now blend the grass overlay onto the body result
        # Create grass overlay
        overlay = body_result.copy()
        overlay[grass_mask > 0] = [0, 255, 0]
        
        # Blend: 85% body result, 15% grass overlay (more transparent grass so body shows through)
        final_result = cv2.addWeighted(body_result, 0.85, overlay, 0.15, 0)

        y_offset = 30
        for part, in_contact in contact_status.items():
            status_text = f"{part}: {'Contact' if in_contact else 'No Contact'}"
            color = (0, 255, 0) if in_contact else (100, 100, 100)
            cv2.putText(final_result, status_text, (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y_offset += 25

        # display processed frame
        cv2.imshow('full body detection', final_result)

        # temporary quit key
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

# release resources
cap.release()
cv2.destroyAllWindows()
