import cv2 as cv 
import numpy as np 
import os 
import matplotlib.pyplot as plt 
import mediapipe as mp
import pyautogui as pg

def get_right_eyebox(frame):
    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    screen_w, screen_h = pg.size()

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
        # We are considering only one face that is closest to camera
        landmarks = face_landmarks[0].landmark

        # Landmarks are selected to make a rectangle around the right eye as ROI
        points = [landmarks[340], landmarks[301], landmarks[6], landmarks[9]]
        

        x_points = []
        y_points = []

        # Looping through the points list and append the x and y coordinates of each landmark to the x_points and y_points lists
        for point in points:
            x_points.append(int(point.x * frame_w))
            y_points.append(int(point.y * frame_h))
        print(f"x_points: {x_points}\ny_points: {y_points}")
        # Find the minimum and maximum x and y coordinates of the rectangle
        min_x = min(x_points)
        max_x = max(x_points)
        min_y = min(y_points)
        max_y = max(y_points)

        ################## IMAGE CROPING TO GET BOUNDING BOX ##########################
        eye_box = frame[min_y:max_y, min_x:max_x]
        eye_box = cv.resize(eye_box, (128, 128))
        return eye_box
    return None


def lucasKanade():
    # Setup parameters 
    shiTomasiCornerParams = dict(maxCorners=20,
                                 qualityLevel=0.3,
                                 minDistance=50,
                                 blockSize=7 )

    lucasKanadeParams = dict(winSize=(15, 15),
                             maxLevel=2,
                             criteria=(cv.TERM_CRITERIA_EPS|cv.TERM_CRITERIA_COUNT,10,0.03))

    randomColors = np.random.randint(0,255,(100, 3))

    # Initialize camera capture
    cap = cv.VideoCapture(0)

    # Find features to track
    try:
        _, frame = cap.read()
        right_eyebox = get_right_eyebox(frame)
        if right_eyebox is None:
            raise ValueError("Right eye box not found")
        frameGrayPrev = cv.cvtColor(right_eyebox, cv.COLOR_BGR2GRAY)
        cornersPrev = cv.goodFeaturesToTrack(frameGrayPrev, mask=None, **shiTomasiCornerParams)
        mask = np.zeros_like(right_eyebox)
        img = right_eyebox.copy()

        # Initialize a variable to count consecutive failed frames
        failed_frame_count = 0

        # Loop through each video frame
        while True:
            _, frame = cap.read()
            right_eyebox = get_right_eyebox(frame)
            if right_eyebox is None:
                failed_frame_count += 1
                if failed_frame_count > 10:  # Adjust the threshold as needed
                    print("Exceeded maximum consecutive failed frames. Exiting loop.")
                    break
                continue
            frameGrayCur = cv.cvtColor(right_eyebox, cv.COLOR_BGR2GRAY)
            cornersCur, foundStatus, _ = cv.calcOpticalFlowPyrLK(frameGrayPrev,frameGrayCur,cornersPrev,None, **lucasKanadeParams)

            if cornersCur is not None:
                cornersMatchedCur = cornersCur[foundStatus==1]
                cornersMatchedPrev = cornersPrev[foundStatus==1]

                # Reset failed frame count
                failed_frame_count = 0

            for i, (curCorner, prevCorner) in enumerate(zip(cornersMatchedCur, cornersMatchedPrev)):
                xCur, yCur = curCorner.ravel()
                xPrev, yPrev = prevCorner.ravel()
                mask = cv.line(mask,(int(xCur),int(yCur)),(int(xPrev),int(yPrev)),randomColors[i].tolist(),2)
                right_eyebox = cv.circle(right_eyebox, (int(xCur), int(yCur)),5,randomColors[i].tolist(),-1)
                img = cv.add(right_eyebox,mask)

            cv.imshow('Video',img)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

            frameGrayPrev = frameGrayCur.copy()
            cornersPrev = cornersMatchedCur.reshape(-1,1,2)
    except Exception as e:
        print(f"An error occurred while finding eye in the frame: {e}")
    finally:
        cap.release()
        cv.destroyAllWindows()

if __name__ == '__main__':
    lucasKanade()
