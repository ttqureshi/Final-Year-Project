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

    if (t1-t >= 1): # 'and (t1-t <= 16)' 
        if (time_lapsed >= 1.0/frame_rate):
            prev = time.time()
            cv.imshow('Video', frame)

            # Sharpening the video frame
            kernel = np.array([[0, -1, 0], [-1, 9.5, -1], [0, -1, 0]])
            sharpened = cv.filter2D(frame, -1, kernel)
            cv.imshow('Sharpened Frame', sharpened)

            gray = cv.cvtColor(sharpened, cv.COLOR_BGR2GRAY)

            eyes_rect = haar_cascade_eye.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=15)
            face_rect = haar_cascade_face.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            
            
            # eye_rect_start = tuple(eyes_rect[0][:2])
            # eye_rect_end = tuple(eyes_rect[1][:2] + eyes_rect[1][2:])
            # cv.rectangle(frame, eye_rect_start, eye_rect_end, (0,255,0), thickness=2)


            # enboxing all faces in blue color just to see that face is being detected
            for (x,y,w,h) in face_rect:
                cv.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), thickness=2)

            # enboxing the face (with the color: (255,255,0)) closest to the camera...ignoring the rest. it's the only face which will be sent to further processing
            if (len(face_rect)>=1 or len(eyes_rect)>=2):
                mul_last_two_elements = lambda row : row[-2] * row[-1] # implemnted for the purpose of getting the area of box around the face. The shape of 'face_rect' is (n,4). Where 'n' is the number of faces detected and 4 are the 'x-coord, y-coord, width and height' respectively. This function multiplies the last two elements (width and height) to get the area.
                # def mul_last_two_elements(row):
                #     return row[-2] * row[-1]
                
                # getting the index of face closest to the camera
                i = np.argmax(np.apply_along_axis(mul_last_two_elements, axis=1, arr=face_rect))
                f_x,f_y,f_w,f_h = face_rect[i]
                cv.rectangle(frame, (f_x,f_y), (f_x+f_w, f_y+f_h), (255,255,0), thickness=2)

                # eyes detected in the face closest to the camera.
                if (len(eyes_rect)>1):
                    





            for (x,y,w,h) in eyes_rect:
                cv.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), thickness=2)
            
            

            cv.imshow('Detected Face and Eyes', frame)
            cv.imwrite(f'temp/{int(t1-t)}_{frames_cap}.jpg',frame)
        frames_cap += 1

    if cv.waitKey(1) & 0xFF == ord('d'):
        break

capture.release()
cv.destroyAllWindows()