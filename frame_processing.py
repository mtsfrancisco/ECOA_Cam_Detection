import cv2
import numpy as np

# To make video slower and visible
def create_delay(capture):
    fps = capture.get(cv2.CAP_PROP_FPS)
    slow_factor = 2  # Change this value to control the slow speed
    delay = int(1000 / (fps / slow_factor))
    return delay

def adjust_gamma(image, gamma = 1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	inv_gamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** inv_gamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)

def basic_threshold(frame, gamma = 1.0):
    kernel = np.ones((5,5),np.uint8)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(frame, (5,5), 0)
    _, frame = cv2.threshold(frame, 80, 190, cv2.THRESH_BINARY_INV)
    frame = cv2.dilate(frame, kernel, iterations=1)
    return frame