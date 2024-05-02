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
        dict: The modified dictionary `iris_calibrations` with parallax corrected coordinates for each position.
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
        list: A new NumPy array of shape (2,) containing the transformed x and y coordinates.
    """
    new_point = point - ref_origin
    new_point[1] = -1 * new_point[1]

    return new_point

def get_iris_center(frame, face_mesh):
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

def get_vec_mag(vector):
    """
    Parameters
    ----------
    vector : 1D numpy array

    Returns
    -------
    mag : The magnitude of input vector (1D numpy array)
    """
    mag = math.sqrt(sum(pow(element, 2) for element in vector))
    return mag

def get_unit_vec(vector):
    """
    Uses the get_vec_mag() function and returns the unit vector
    """
    mag = get_vec_mag(vector)
    return vector/mag 

def main():
    f = open('iris_calibrations.json')
    iris_calibrations = json.load(f)
    f.close()

    # Remove Parallax
    iris_calibrations = remove_parallax(iris_calibrations)

    # save the old origin value
    old_origin = np.array(iris_calibrations['midcenter'])

    eye_box_width  = abs(iris_calibrations['midright'][0] - iris_calibrations['midleft'][0])
    eye_box_height = abs(iris_calibrations['topcenter'][1] - iris_calibrations['bottomcenter'][1])

    screen_w, screen_h = pg.size()

    eyebox_1_unit_in_x = screen_w // eye_box_width  # 1 unit along x-axis in eyebox coordinate system equals screen_w // eye_box_width
    eyebox_1_unit_in_y = screen_h // eye_box_height # 1 unit along y-axis in eyebox coordinate system equals screen_h // eye_box_height
    eyebox_1_unit_in_xy = np.array([eyebox_1_unit_in_x, eyebox_1_unit_in_y])

    # translate and vertically flip the coordinate system
    positions = ['topleft', 'topcenter', 'topright', 'midleft', 'midcenter', 'midright', 'bottomleft', 'bottomcenter', 'bottomright']
    iris_calibrations_translated = {} # translated and vertically flipped coordinate system

    for position in positions:
        point = np.array(iris_calibrations[position])
        new_point = list(translate_and_vflip_coordinate(point, old_origin))
        iris_calibrations_translated[position] = new_point

    cap = cv.VideoCapture(0)
    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

    pg.FAILSAFE = False

    # v_ks, a numpy array of shape (8,2), where i-th row in v_ks is the i-th quantized direction
    v_ks = np.array([
        [ 1, 0], # right
        [ 1, 1], # diagnoal up-right
        [ 0, 1], # up
        [-1, 1], # diagonal up-left
        [-1, 0], # left
        [-1,-1], # diagonal down-left
        [ 0,-1], # down
        [ 1,-1]  # diagonal down-right
        ])
    
    # unit_v_ks => ndarray of shape same as v_ks, containing the unit direction vectors 
    unit_v_ks = np.apply_along_axis(get_unit_vec, axis=1, arr=v_ks)

    _, frame = cap.read()
    prev_iris_center = np.array(get_iris_center(frame, face_mesh))
    prev_iris_pos_vec = translate_and_vflip_coordinate(prev_iris_center, old_origin)

    frame_timeout = 1
    count = 0
    try:
        while True:
            _, frame = cap.read()
            count += 1

            if count > frame_timeout:
                count = 0
                curr_iris_center = np.array(get_iris_center(frame, face_mesh))
                curr_iris_pos_vec = translate_and_vflip_coordinate(curr_iris_center, old_origin)

                diff_vec = curr_iris_pos_vec - prev_iris_pos_vec
                prev_iris_pos_vec = curr_iris_pos_vec

                diff_vec_mag = int(get_vec_mag(diff_vec))
                diff_unit_vec = get_unit_vec(diff_vec)

                dots = np.array([np.dot(diff_unit_vec, unit_vk) for unit_vk in unit_v_ks])
                closest_quant_dir = v_ks[np.argmax(dots)]

                scaled = diff_vec_mag * eyebox_1_unit_in_xy
                x_sign = int(math.copysign(1.0, closest_quant_dir[0]))
                y_sign = int(math.copysign(1.0, closest_quant_dir[1]))

                scaled[0] = x_sign * scaled[0]
                scaled[1] = (y_sign * scaled[1])

                cursor_cur_x, cursor_cur_y = pg.position()
                new_x = cursor_cur_x + scaled[0]
                new_y = cursor_cur_y + scaled[1]
                pg.moveTo(new_x, new_y)


    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        cap.release()
        cv.destroyAllWindows()