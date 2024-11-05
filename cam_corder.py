import cv2
import imutils
import numpy as np
import argparse
from matplotlib import pyplot as plt
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

def create_delay(capture):
    fps = capture.get(cv2.CAP_PROP_FPS)
    slow_factor = 2  # Change this value to control the slow speed
    delay = int(1000 / (fps / slow_factor))
    return delay


# Main ----------------------------------------------------------------------
cap = get_video("./media/TestVideo.mp4")
delay = create_delay(cap)
while True:
    # Capturing image frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break




    frame = imutils.resize(frame, width=1200)

    # Matheus Method // Yolo

    # Cury Method

    # Enzo Method // WaterShed/CountingContours
    thresh_frame = basic_threshold(frame, 0.5)
    sharp_frame = create_sharp_frame(frame)
    water_shed_frame = water_shed(frame, thresh_frame, sharp_frame)
    boxed_frame = draw_boxes(frame.copy(), water_shed_frame, 15000)
    cv2.imshow("Boxed", boxed_frame)

    # Breaking the loop if the key 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
