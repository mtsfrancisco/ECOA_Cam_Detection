import cv2
import numpy as np

# To make video slower and visible


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

    frame = adjust_gamma(frame, gamma)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(frame, (5,5), 0)
    _, frame = cv2.threshold(frame, 50, 230, cv2.THRESH_BINARY_INV)
    frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
    return frame