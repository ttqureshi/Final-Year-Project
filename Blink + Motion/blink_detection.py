import cv2
import mediapipe as mp
import numpy as np

cam = cv2.VideoCapture(0)
# cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# function to detect the vertical distance between the upper and lower eyelids
def is_blink(landmarks, frame_w, frame_h):
    # Define the right eye landmarks for upper and lower eyelids
    upper_lid = landmarks[386]  # Top of the right eye
    lower_lid = landmarks[374]  # Bottom of the right eye

    # screen coordinates
    upper_y = int(upper_lid.y * frame_h)
    lower_y = int(lower_lid.y * frame_h)

    # Calculating vertical distance
    vertical_distance = lower_y - upper_y
    return vertical_distance


blink_state = 'open'  # Initial state of the eye
blink_start = 0
closure_threshold = 5  # Threshold for eye closure 
reopen_threshold = 6  # Threshold for eye reopening 

while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    frame_h, frame_w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    output = face_mesh.process(rgb_frame)
    face_landmarks = output.multi_face_landmarks

    if face_landmarks:
        landmarks = face_landmarks[0].landmark # getting the first face landmarks 
        
        # Check if eyes are closed or not
        eye_distance = is_blink(landmarks, frame_w, frame_h)

        if blink_state == 'open' and eye_distance < closure_threshold:
            blink_state = 'closing'
            blink_start = cv2.getTickCount()

        elif blink_state == 'closing' and eye_distance >= reopen_threshold:
            blink_end = cv2.getTickCount()
            blink_duration = (blink_end - blink_start) / cv2.getTickFrequency()

            if 0.25 <= blink_duration <= 1.2:
                print("Intentional Blink Detected!")
            blink_state = 'open'

        elif blink_state == 'closing' and eye_distance < closure_threshold:
            blink_state = 'closed'

        elif blink_state == 'closed' and eye_distance >= reopen_threshold:
            blink_end = cv2.getTickCount()
            blink_duration = (blink_end - blink_start) / cv2.getTickFrequency()

            if 0.25 <= blink_duration <= 1.2:
                print("Intentional Blink Detected!")
            blink_state = 'open'
    
    # Resulting frame            
    state = "state: " + blink_state
    cv2.putText(frame, state, (10, 30), cv2.FONT_HERSHEY_TRIPLEX, 1, (120, 65, 148), 2)
    cv2.imshow("A moving cursor using Eye ball movement", frame)

    # Exit condition
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cam.release()
cv2.destroyAllWindows()
