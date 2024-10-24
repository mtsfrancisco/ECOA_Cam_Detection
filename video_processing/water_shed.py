import cv2
import numpy as np
import argparse
import math
import imutils
from matplotlib import pyplot as plt

def water_shed_1(original_frame, threshed_frame):
    # noise removal
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(threshed_frame,cv2.MORPH_OPEN,kernel, iterations = 2)

    # sure background area
    sure_bg = cv2.dilate(opening,kernel,iterations=3)

    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,3)
    ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)

    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    #cv2.imshow("sure fore", sure_fg)
    #cv2.imshow("sure fback", sure_bg)
    unknown = cv2.subtract(sure_bg,sure_fg)

    #cv2.imshow("unknown", unknown)
    # Marker labelling
    ret, markers = cv2.connectedComponents(sure_fg)
    
    #cv2.imshow("markers", markers)
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers+1

    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0
    markers = cv2.watershed(original_frame, markers)
    original_frame[markers == -1] = [255,0,0]
    #cv2.imshow("Water2", original_frame)
    return original_frame

def drawBoxes(original_frame, threshed_frame):
    contours, _ = cv2.findContours(threshed_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours: 
        area = cv2.contourArea(cnt)
        if area > 100:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(original_frame, (x,y), (x + w, y+ h), (0, 255, 0), 3)

    return original_frame