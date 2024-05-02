import numpy as np
import cv2 as cv
import mediapipe as mp
import pyautogui as pg
import json
import math

def remove_parallax(iris_calibrations):
    """
    Removes parallax effect from the provided iris calibration data.
    This function corrects for potential misalignment between the user's head position and the screen during calibration.
    It achieves this by finding the minimum and maximum x and y coordinates across specific calibration points ('topleft', 'midleft', 'bottomleft' for left edge, and similarly for right and top/bottom edges). 
    It then adjusts all calibration points to have a straightened bounding box based on these corrected edges.

    Args:
        iris_calibrations (dict): A dictionary containing iris center coordinates for different screen positions (e.g., 'topleft': [x, y], 'midcenter': [x, y]).

    Returns:
        iris_calibrations (dict): The modified dictionary `iris_calibrations` with parallax corrected coordinates for each position.
    """
    
    left_edge_x = min(round(iris_calibrations['topleft'][0]),
                      round(iris_calibrations['midleft'][0]),
                      round(iris_calibrations['bottomleft'][0]))
    mid_line_x = (round(iris_calibrations['midleft'][0]) + round(iris_calibrations['midcenter'][0]) + round(iris_calibrations['midright'][0])) // 3
    right_edge_x = max(round(iris_calibrations['topright'][0]),
                       round(iris_calibrations['midright'][0]),
                       round(iris_calibrations['bottomright'][0]))
    
    upper_edge_y = min(round(iris_calibrations['topleft'][1]),
                      round(iris_calibrations['midleft'][1]),
                      round(iris_calibrations['bottomleft'][1]))
    mid_line_y = (round(iris_calibrations['midleft'][1]) + round(iris_calibrations['midcenter'][1]) + round(iris_calibrations['midright'][1])) // 3
    bottom_edge_y = max(round(iris_calibrations['topright'][1]),
                       round(iris_calibrations['midright'][1]),
                       round(iris_calibrations['bottomright'][1]))
    
    iris_calibrations['topleft'] = [left_edge_x, upper_edge_y]
    iris_calibrations['topcenter'] = [mid_line_x, upper_edge_y]
    iris_calibrations['topright'] = [right_edge_x, upper_edge_y]

    iris_calibrations['midleft'] = [left_edge_x, mid_line_y]
    iris_calibrations['midcenter'] = [mid_line_x, mid_line_y]
    iris_calibrations['midright'] = [right_edge_x, mid_line_y]

    iris_calibrations['bottomleft'] = [left_edge_x, bottom_edge_y]
    iris_calibrations['bottomcenter'] = [mid_line_x, bottom_edge_y]
    iris_calibrations['bottomright'] = [right_edge_x,  bottom_edge_y]

    return iris_calibrations

def translate_and_vflip_coordinate(point, ref_origin):
    """
    Translates and vertically flips a coordinate point based on a reference origin (NumPy arrays).
    This function takes a coordinate point (represented as a NumPy array with x and y values) and an old origin point (also a NumPy array). It performs the following:

    1. Translation: Subtracts the old origin coordinates from the point coordinates (element-wise subtraction).
    2. Vertical Flip: Negates the y-coordinate value in the point array, essentially flipping the point along the horizontal axis.

    Args:
        point (numpy.ndarray): A NumPy array containing the x and y coordinates of the point to be transformed (shape: (2,)).
        old_origin (numpy.ndarray): A NumPy array representing the reference origin point (x and y coordinates) (shape: (2,)).

    Returns:
        new_point (list): A new NumPy array of shape (2,) containing the transformed x and y coordinates.
    """
    new_point = point - ref_origin
    new_point[1] = -1 * new_point[1]

    return new_point

def get_iris_center(frame, face_mesh):
    """
    Extracts the iris center coordinates from a given frame using a face mesh model.

    Args:
        frame (numpy.ndarray): The input frame (image) as a NumPy array (BGR color format).
        face_mesh (object): A face mesh detection object (from MediaPipe).

    Returns:
        center (list): A list containing the iris center coordinates [x, y] if a face is detected, None otherwise.
    """
    frame = cv.flip(frame, 1)
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    output = face_mesh.process(frame)
    face_landmarks = output.multi_face_landmarks

    frame_h, frame_w, _ = frame.shape

    if face_landmarks:
        landmarks = face_landmarks[0].landmark
        iris_center = landmarks[473]

        x = iris_center.x * frame_w
        y = iris_center.y * frame_h
    center = [x,y]
    return center

def calc_eye_vertical_dist(frame, face_mesh):
    """
    Calculates the vertical distance between the upper and lower eyelid of the right eye.

    Args:
        frame (numpy.ndarray): The input frame (image) as a NumPy array (BGR color format).
        face_mesh (object): A face mesh detection object (e.g., from MediaPipe).

    Returns:
        vertical_distance (int): The vertical distance between the upper and lower eyelid (in pixels) if a face is detected, None otherwise.
    """
    frame = cv.flip(frame, 1)
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    output = face_mesh.process(frame)
    face_landmarks = output.multi_face_landmarks

    frame_h, frame_w, _ = frame.shape

    if face_landmarks:
        landmarks = face_landmarks[0].landmark
        upper_lid = landmarks[386] # Top of the right eye
        lower_lid = landmarks[374] # Bottom of the right eye

        upper_y = int(upper_lid.y * frame_h)
        lower_y = int(lower_lid.y * frame_h)

        vertical_distance = lower_y - upper_y
    return vertical_distance

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

def main():
    f = open('iris_calibrations.json')
    iris_calibrations = json.load(f)
    f.close()
    print(f"Before removing parallax: {iris_calibrations}\n")

    # Remove Parallax
    iris_calibrations = remove_parallax(iris_calibrations)
    print(f"Removed parallax from calibration data: {iris_calibrations}")


    origin = np.array(iris_calibrations['midcenter'])

    screen_w, screen_h = pg.size()

    positions = ['topleft', 'topcenter', 'topright', 'midleft', 'midcenter', 'midright', 'bottomleft', 'bottomcenter', 'bottomright']

    f = open('eye_vertical_dist.json')
    eye_vertical_dist = json.load(f)
    f.close()

    eye_vertical_dist_thresh = 10000
    for position in positions:
        eye_vertical_dist_thresh = min(eye_vertical_dist_thresh, eye_vertical_dist[position])
    print(f"\neye_vertical_dist_thresh={eye_vertical_dist_thresh}\n")

    cap = cv.VideoCapture(0)
    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

    pg.FAILSAFE = False

    _, frame = cap.read()

    f = open("quadrants.json")
    quadrants = json.load(f)
    f.close()

    blink_state = 'open' # Initial state of the eye
    blink_start = 0
    closure_threshold = eye_vertical_dist_thresh // 2

    try:
        while True:
            _, frame = cap.read()
            vertical_dist = calc_eye_vertical_dist(frame, face_mesh)
            # count += 1
            count = 0
            if (vertical_dist >= eye_vertical_dist_thresh):
                curr_iris_center = np.array(get_iris_center(frame, face_mesh))

                if curr_iris_center[0]>origin[0] and curr_iris_center[1]<origin[1]:
                    pg.moveTo(quadrants["q1"][0],quadrants["q1"][1])
                elif curr_iris_center[0]<origin[0] and curr_iris_center[1]<origin[1]:
                    pg.moveTo(quadrants["q2"][0],quadrants["q2"][1])
                    
                elif curr_iris_center[0]<origin[0] and curr_iris_center[1]>origin[1]:
                    pg.moveTo(quadrants["q3"][0],quadrants["q3"][1])
                    
                elif curr_iris_center[0]>origin[0] and curr_iris_center[1]>origin[1]:
                    pg.moveTo(quadrants["q4"][0],quadrants["q4"][1])
            
            frame = cv.flip(frame, 1)
            frame_h, frame_w, _ = frame.shape
            rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

            output = face_mesh.process(rgb_frame)
            face_landmarks = output.multi_face_landmarks

            if face_landmarks:
                landmarks = face_landmarks[0].landmark # getting the first face landmarks

                # Check if eyes are closed or not
                eye_distance = is_blink(landmarks, frame_w, frame_h)

                if blink_state == 'open' and eye_distance < closure_threshold:
                    blink_state = 'closing'
                    blink_start = cv.getTickCount()

                elif blink_state == 'closing' and eye_distance >= closure_threshold:
                    blink_end = cv.getTickCount()
                    blink_duration = (blink_end - blink_start) / cv.getTickFrequency()

                    if 0.25 <= blink_duration <= 1.2:
                        print("Intentional Blink Detected!")
                        pg.click()
                    blink_state = 'open'

                elif blink_state == 'closing' and eye_distance < closure_threshold:
                    blink_state = 'closed'

                elif blink_state == 'closed' and eye_distance >= closure_threshold:
                    blink_end = cv.getTickCount()
                    blink_duration = (blink_end - blink_start) / cv.getTickFrequency()

                    if 0.25 <= blink_duration <= 1.2:
                        print("Intentional Blink Detected!")
                        pg.click()
                    blink_state = 'open'
            
            # Resulting frame
            state = "state: " + blink_state
            cv.putText(frame, state, (10, 30), cv.FONT_HERSHEY_TRIPLEX, 1, (120, 65, 148), 2)
            cv.imshow("A moving cursor using Eye ball movement", frame)

            if cv.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        cap.release()
        cv.destroyAllWindows()