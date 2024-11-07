import cv2
import numpy as np
import argparse
import math
import imutils
from matplotlib import pyplot as plt


def create_sharp_frame(frame):
    kernel = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]], dtype=np.float32)

    imgLaplacian = cv2.filter2D(frame, cv2.CV_32F, kernel)
    sharp = np.float32(frame)
    imgResult = sharp - imgLaplacian
    # convert back to 8bits gray scale
    imgResult = np.clip(imgResult, 0, 255)
    imgResult = imgResult.astype('uint8')
    imgLaplacian = np.clip(imgLaplacian, 0, 255)
    imgLaplacian = np.uint8(imgLaplacian)
    #cv.imshow('Laplace Filtered Image', imgLaplacian)
    #cv2.imshow('New Sharped Image', imgResult)

    return imgResult

def water_shed(frame, opening, imgResult):
    kernel = np.ones((5,5),np.uint8)
    sure_bg = cv2.dilate(opening,kernel,iterations=3)
 
    cv2.imshow("opening", opening)
    # Finding sure foreground area
    dist = cv2.distanceTransform(opening, cv2.DIST_L2, 3)
    cv2.normalize(dist, dist, 0, 1.0, cv2.NORM_MINMAX)
    #cv2.imshow('Distance Transform Image', dist)




    # Step to focus on
    _, dist = cv2.threshold(dist, 0.3, 1.0, cv2.THRESH_BINARY)
    dist = cv2.dilate(dist, kernel)
    # Opening to remove a LOT of noise
    eroded = cv2.erode(dist,kernel,iterations = 1)
    opening = cv2.dilate(eroded,kernel,iterations = 1)
    cv2.imshow('Peaks', opening)


    #cv2.imshow('Opening', opening)





    dist_8u = opening.astype('uint8')
    # Find total markers
    contours, _ = cv2.findContours(dist_8u, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Create the marker image for the watershed algorithm
    markers = np.zeros(dist.shape, dtype=np.int32)
    # Draw the foreground markers
    for i in range(len(contours)):
        cv2.drawContours(markers, contours, i, (i+1), -1)

    # Draw the background marker
    cv2.circle(markers, (5,5), 3, (255,255,255), -1)
    markers_8u = (markers * 10).astype('uint8')
    #cv2.imshow('Markers', markers_8u)

    cv2.watershed(frame, markers)
    mark = markers.astype('uint8')
    mark = cv2.bitwise_not(mark)
    #cv2.imshow('Markers_v2', mark)

    _, mark = cv2.threshold(mark, 50, 230, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)


    return mark

def draw_boxes(original_frame, threshed_frame, max_area):
    contours, _ = cv2.findContours(threshed_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours: 
        area = cv2.contourArea(cnt)
        if 1000 < area < max_area:  # Draw boxes only for areas within the range
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(original_frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

    return original_frame
