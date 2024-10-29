import cv2
import imutils
import numpy as np
from frame_processing import *
from video_processing.water_shed import * 

# Global variables ---------------------------------------------------------


# Functions ----------------------------------------------------------------
def get_video(video_path):
    capture = cv2.VideoCapture(video_path) # Capture Video

    if not capture.isOpened():
        print("Error: Could not open video.")
        exit()

    return capture



# Main ----------------------------------------------------------------------
capture = get_video("./media/TestVideo.mp4")
delay = create_delay(capture)
while True:
    # Capturing image frame-by-frame
    ret, frame = capture.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break




    frame = imutils.resize(frame, width=1200)

    # Matheus Method // Yolo

    # Cury Method

    # Enzo Method // WaterShed/CountingContours
    gamma_frame = adjust_gamma(frame)
    thresh_frame = basic_threshold(gamma_frame)
    water_shed_frame = water_shed_1(frame, thresh_frame)

    # Breaking the loop if the key 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()