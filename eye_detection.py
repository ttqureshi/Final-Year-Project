import numpy as np
import cv2 as cv
import time


capture = cv.VideoCapture(0)
# capture.set(3, 500)
# capture.set(4, 700)
# capture.set(10, 90)

haar_cascade_face = cv.CascadeClassifier('haar_face.xml')
haar_cascade_eye = cv.CascadeClassifier('haarcascade_eye.xml')


frame_rate = 5 # required frame rate
prev = 0
frames_cap = 0
t = time.time()

while True:
    _, frame = capture.read()
    t1 = time.time()
    time_lapsed = t1 - prev

    if (t1-t >= 1 and t1-t < 5):
        if (time_lapsed >= 1.0/frame_rate):
            prev = t1
            cv.imshow('Video', frame)

            # Sharpening the video frame
            kernel = np.array([[0, -1, 0], [-1, 10, -1], [0, -1, 0]])
            sharpened = cv.filter2D(frame, -1, kernel)
            cv.imshow('Sharpened Frame', sharpened)

            gray = cv.cvtColor(sharpened, cv.COLOR_BGR2GRAY)

            eyes_rect = haar_cascade_eye.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=15)
            face_rect = haar_cascade_face.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            
            
            # eye_rect_start = tuple(eyes_rect[0][:2])
            # eye_rect_end = tuple(eyes_rect[1][:2] + eyes_rect[1][2:])
            # cv.rectangle(frame, eye_rect_start, eye_rect_end, (0,255,0), thickness=2)


            for (x,y,w,h) in eyes_rect:
                cv.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), thickness=2)
            
            
            for (x,y,w,h) in face_rect:
                cv.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), thickness=2)

            cv.imshow('Detected Face and Eyes', frame)
            cv.imwrite(f'temp/{int(t1-t)}_{frames_cap}.jpg',frame)
        frames_cap += 1

    if cv.waitKey(1) & 0xFF == ord('d'):
        break

capture.release()
cv.destroyAllWindows()