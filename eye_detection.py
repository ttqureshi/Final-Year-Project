import numpy as np
import cv2 as cv
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
    # print(f'FACE:\n{face_rect}')
    # print(f'# of faces detected: {len(face_rect)}\n')

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


frame_rate = 10 # required frame rate
prev = 0
time_limit = 2 # get the eye coordinates every n=(time_limit*frame_rate) frames. Here time_limit is in seconds
# t = 0
counter = 0
num_of_times_eye_coord_calculated = 0
num = 0

start_time = time.time()
while True:
    isTrue, frame = capture.read()
    if frame is not None:
        cv.imshow('Frame', frame)
    t1 = time.time()
    time_lapsed = t1 - prev

    if (time_lapsed >= 1.0/frame_rate):
        prev = time.time()
        counter+=1
        
        if frame is not None and frame.size > 0:
            # time_since_last_check = time.time() - t
            num += 1
            if (counter % (time_limit*frame_rate) == 1):
                # t = time.time()
                eyes_rect = get_eyebox_coord(frame, haar_cascade_face, haar_cascade_eye)
                num_of_times_eye_coord_calculated += 1
        else:
            break
        
        if (len(eyes_rect) != 0):
            x, y, w, h = eyes_rect[0]
            eye_cropped = frame[x-20:x+w+20, y:y+h+40]
            cv.imshow("eye", eye_cropped)
        # counter += 1
        
    if cv.waitKey(100) & 0xFF==ord('d'):
        break

print(f"Time taken: {time.time()-start_time}")
print(counter)
print(f'number of times eye coord calculated: {num_of_times_eye_coord_calculated}')
print(num)
capture.release()
cv.destroyAllWindows()