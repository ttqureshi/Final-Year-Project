import cv2 as cv
import numpy as np
import dlib

# Initialize dlib's face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Function to detect and return the iris region within the eye region
def get_iris(image, eye_region):
    # Define a region of interest (ROI) around the eye region
    (x, y, w, h) = cv.boundingRect(np.array([eye_region]))
    roi = image[y:y+h, x:x+w]

    # Perform iris segmentation using image processing techniques
    # You can replace this with a more advanced iris segmentation algorithm if needed
    gray_roi = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
    _, iris = cv.threshold(gray_roi, 30, 255, cv.THRESH_BINARY)

    return iris

# Function to track iris motion using Lucas-Kanade optical flow
def track_iris(prev_frame, prev_iris, curr_frame):
    # Convert frames to grayscale
    prev_gray = cv.cvtColor(prev_frame, cv.COLOR_BGR2GRAY)
    curr_gray = cv.cvtColor(curr_frame, cv.COLOR_BGR2GRAY)

    # Calculate optical flow using Lucas-Kanade method
    optical_flow = cv.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    # Apply the optical flow to previous iris region to track its motion
    h, w = prev_iris.shape[:2]
    new_iris_pts = np.array([[x, y] + optical_flow[y, x] for x in range(0, w, 5) for y in range(0, h, 5)], dtype=np.float32).reshape(-1, 1, 2)
    new_iris_pts = np.clip(new_iris_pts, 0, [w, h])

    return new_iris_pts

# Main function for iris motion tracking
def iris_motion_tracking():
    # Initialize video capture
    cap = cv.VideoCapture(0)

    # Initialize previous frame and iris region
    _, prev_frame = cap.read()
    prev_iris = np.zeros_like(prev_frame[:, :, 0])

    while True:
        # Capture current frame
        ret, curr_frame = cap.read()
        if not ret:
            break

        # Detect face and eyes using dlib
        gray = cv.cvtColor(curr_frame, cv.COLOR_BGR2GRAY)
        faces = detector(gray)
        for face in faces:
            landmarks = predictor(gray, face)
            right_eye_region = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
            left_eye_region = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])

            # Get iris regions for both eyes
            right_iris = get_iris(curr_frame, right_eye_region)
            left_iris = get_iris(curr_frame, left_eye_region)

            # Track iris motion using optical flow
            new_right_iris_pts = track_iris(prev_frame, prev_iris, curr_frame)
            new_left_iris_pts = track_iris(prev_frame, prev_iris, curr_frame)

            # Draw optical flow tracks on the current frame
            for pt in new_right_iris_pts:
                x, y = pt.ravel()
                cv.circle(curr_frame, (x, y), 1, (0, 255, 0), -1)
            for pt in new_left_iris_pts:
                x, y = pt.ravel()
                cv.circle(curr_frame, (x, y), 1, (0, 255, 0), -1)

        # Display current frame
        cv.imshow('Iris Motion Tracking', curr_frame)

        # Update previous frame and iris region
        prev_frame = curr_frame.copy()
        prev_iris = right_iris.copy()  # You can choose either right or left iris for tracking

        # Exit loop if 'q' is pressed
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    # Release video capture and close all windows
    cap.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    iris_motion_tracking()
