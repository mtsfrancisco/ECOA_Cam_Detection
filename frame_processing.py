import cv2
import numpy as np

# To make video slower and visible
def createDelay(capture):
    fps = capture.get(cv2.CAP_PROP_FPS)
    slow_factor = 2  # Change this value to control the slow speed
    delay = int(1000 / (fps / slow_factor))
    return delay

