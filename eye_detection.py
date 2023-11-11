import numpy as np
import cv2 as cv
import os

img = cv.imread('imgs/man.jpg')
cv.imshow('Image', img)
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
cv.imshow('Gray', gray)

haar_cascade_eye = cv.CascadeClassifier('haarcascade_eye.xml')
eyes_rect = haar_cascade_eye.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=8)

print(f'Number of eyes found: {len(eyes_rect)}')
print(eyes_rect)

# Drawing rectangles around eyes
for (x,y,w,h) in eyes_rect:
    cv.rectangle(img, (x,y), (x+w,y+h), (0,255,0), thickness=2)



haar_cascade_face = cv.CascadeClassifier('haar_face.xml')
face_rect = haar_cascade_face.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=1)

print(f'Number of faces found: {len(face_rect)}')
print(face_rect)

# Drawing rectangle around face
for (x,y,w,h) in face_rect:
    cv.rectangle(img, (x,y), (x+w,y+h), (255,0,0), thickness=2)

cv.imshow('Detected face and eyes', img)


cv.waitKey(0)
cv.destroyAllWindows()





capture = cv.VideoCapture(0)
capture.set(3, 500)
capture.set(4, 700)
capture.set(10, 90)

while True:
    success, frame = capture.read()
    cv.imshow('Video', frame)

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    eyes_rect = haar_cascade_eye.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
    face_rect = haar_cascade_face.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2)

    for (x,y,w,h) in eyes_rect:
        cv.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), thickness=2)
    
    for (x,y,w,h) in face_rect:
        cv.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), thickness=2)

    cv.imshow('Detected Face and Eyes', frame)

    if cv.waitKey(1) & 0xFF == ord('d'):
        break

capture.release()
cv.destroyAllWindows()