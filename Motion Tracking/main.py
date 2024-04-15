import cv2 as cv
import pyautogui as pg
import mediapipe as mp

cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

screen_w, screen_h = pg.size()

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

        # Landmarks are selected to make a rectangle around the right eye as ROI
        points = [landmarks[340], landmarks[301], landmarks[6], landmarks[9]]

        x_points = []
        y_points = []
        
        # Looping through the points list and append the x and y coordinates of each landmark to the x_points and y_points lists
        for point in points:
            x_points.append(int(point.x * frame_w))
            y_points.append(int(point.y * frame_h))
        
        # Find the minimum and maximum x and y coordinates of the rectangle
        min_x = min(x_points)
        max_x = max(x_points)
        min_y = min(y_points)
        max_y = max(y_points)

        ################## IMAGE CROPING TO GET BOUNDING BOX ##########################
        
        # Eye box is extracted out to get only right eye
        eye_box1 = frame[min_y:max_y, min_x:max_x]
        cv.imshow('Eye Box', eye_box1)

        # prediction on eyebox
        eye_box = cv.resize(eye_box1, (128, 128))
        eye_box = eye_box.reshape((1, 128, 128, 3))
        


    # cv.imshow('Eye Controlled Mouse', frame)
    if cv.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit the loop
        break











"""
import numpy as np
import cv2 as cv
import pickle
import time
import multiprocessing
import psutil
from concurrent.futures import ProcessPoolExecutor


capture = cv.VideoCapture('blink_eye.mp4')
fps = capture.get(cv.CAP_PROP_FPS)
print(f'fps: {fps}')
total_frames = int(capture.get(cv.CAP_PROP_FRAME_COUNT))
print(f'total frames: {total_frames}')
vid_duration = total_frames/fps
print(f'duration = {vid_duration}')
haar_cascade_face = cv.CascadeClassifier('haar_face.xml')
haar_cascade_eye = cv.CascadeClassifier('haarcascade_eye.xml')

def get_eyebox_coord(frame, haar_cascade_face, haar_cascade_eye):
    kernel = np.array([[0, -1, 0], [-1, 6, -1], [0, -1, 0]])
    sharpened = cv.filter2D(frame, -1, kernel)
    # cv.imshow("Sharpened frame", sharpened)

    gray = cv.cvtColor(sharpened, cv.COLOR_BGR2GRAY)
    face_rect = haar_cascade_face.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x,y,w,h) in face_rect:
        cv.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), thickness=2)

    # enboxing the face (with the color: (255,255,0)) closest to the camera...ignoring the rest. it's the only face which will be sent to further processing
    if (len(face_rect)>1): # if multiple faces
        mul_last_two_elements = lambda row : row[-2] * row[-1] # area of box around the face...The shape of 'face_rect' is (n,4). Where 'n' is the number of faces detected and 4 are the 'x-coord, y-coord, width and height' respectively. This function multiplies the last two elements (width and height) to get the area.
        i = np.argmax(np.apply_along_axis(mul_last_two_elements, axis=1, arr=face_rect)) # index of face closest to the camera
        f_x,f_y,f_w,f_h = face_rect[i]
        cv.rectangle(frame, (f_x, f_y), (f_x+f_w, f_y+f_h), (255,255,0), thickness=2)
        closest_face = frame[f_x:f_x+f_w, f_y:f_y+f_h]
        face_sharpened = cv.filter2D(closest_face, -1, kernel)
        face_gray = cv.cvtColor(face_sharpened, cv.COLOR_BGR2GRAY)
        eyes_rect = haar_cascade_eye.detectMultiScale(face_gray, scaleFactor=1.1, minNeighbors=20)
        
    elif (len(face_rect)==1):
        f_x, f_y, f_w, f_h = face_rect[0]
        cv.rectangle(frame, (f_x, f_y), (f_x+f_w, f_y+f_h), (255,255,0), thickness=2)
        closest_face = frame[f_x:f_x+f_w, f_y:f_y+f_h]
        face_sharpened = cv.filter2D(closest_face, -1, kernel)
        face_gray = cv.cvtColor(face_sharpened, cv.COLOR_BGR2GRAY)
        eyes_rect = haar_cascade_eye.detectMultiScale(face_gray, scaleFactor=1.1, minNeighbors=20)

    for (x,y,w,h) in eyes_rect:
        cv.rectangle(closest_face, (x,y), (x+w,y+h), (0,255,0), thickness=2)
    
    # cv.imshow('Face detected', frame)
    # cv.imshow('Face extracted', closest_face)
    return eyes_rect

is_eye_detected = False
while True:
    isTrue, frame = capture.read()
    if frame is not None:
        cv.imshow('Frame', frame)
    
    if not is_eye_detected:
        eyes_rect = get_eyebox_coord(frame, haar_cascade_face, haar_cascade_eye)
        if len(eyes_rect) > 0:
            is_eye_detected = True
    
    if len(eyes_rect) != 0:
        x, y, w, h = eyes_rect[0]
        eye_cropped = frame[x - 20:x + w + 20, y:y+h+40]
        cv.imshow("eye", eye_cropped)
        model = pickle.load(open('Open Close Eye Classification/model.pkl' , 'rb'))
        prediction = model.predict(eye_cropped)
    
    if cv.waitKey(1) & 0xFF==ord('d'):
        break


capture.release()
cv.destroyAllWindows()
"""