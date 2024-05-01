import cv2 as cv
import pyautogui as pg
import mediapipe as mp

def set_params(face_landmarks):
    landmarks = face_landmarks[0].landmark
    iris_center = landmarks[473]
    prev_x = iris_center.x * frame_w
    prev_y = iris_center.y * frame_h

    # Getting the factor to scale the iris motion to the screen size
    eye_right = landmarks[474] # 466 390
    eye_left = landmarks[476]  # 398 384
    eye_width = abs(eye_right.x*frame_w - eye_left.x*frame_w)

    eye_top = landmarks[385] # 475
    eye_bottom = landmarks[380] # 477
    eye_height = abs(eye_top.y*frame_h - eye_bottom.y*frame_h)

    xscale_factor = screen_w // eye_width
    yscale_factor = screen_h // eye_height

    return prev_x, prev_y, xscale_factor, yscale_factor

cap = cv.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

screen_w, screen_h = pg.size()
pg.FAILSAFE = False

_, prevFrame = cap.read()
prevFrame = cv.flip(prevFrame, 1)
prevFrame = cv.cvtColor(prevFrame, cv.COLOR_BGR2RGB)
frame_h, frame_w, _ = prevFrame.shape
output = face_mesh.process(prevFrame)
face_landmarks = output.multi_face_landmarks

if face_landmarks:
    prev_x, prev_y, xscale_factor, yscale_factor = set_params(face_landmarks)

try:
    while True:
        _, frame = cap.read()
        frame = cv.flip(frame, 1)

        # Convert the frame to RGB
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        # Processing through faceMesh
        output = face_mesh.process(rgb_frame)
        face_landmarks = output.multi_face_landmarks

        # Frame height and width to get necessary scaling
        frame_h, frame_w, _ = frame.shape

        # In case there is a face
        if face_landmarks:
            # We are considering only one face
            landmarks = face_landmarks[0].landmark
            iris_center = landmarks[473]
            cur_x = iris_center.x * frame_w
            cur_y = iris_center.y * frame_h
            # Drawing circles at the current position

            current_cursor_pos = pg.position()
            pg.moveTo(current_cursor_pos.x + (cur_x - prev_x) * xscale_factor, current_cursor_pos.y + (cur_y - prev_y) * yscale_factor, duration=0.2)
            cv.imshow('Eye Controlled Mouse', frame)
            prev_x = cur_x
            prev_y = cur_y
            _, _, xscale_factor, yscale_factor = set_params(face_landmarks)
        
        if cv.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit the loop
            break
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    cap.release()
    cv.destroyAllWindows()
