from math import sqrt

import cv2
import numpy as np
from imutils.contours import sort_contours
from skimage.morphology import skeletonize

from character import Character
from globals import SHOW_STEPS, WAIT_TIME


def get_skeletons(char: Character):
    # Skeletonize the shapes
    # Skimage function takes image with either True, False or 0,1
    # and returns and image with values 0, 1.
    char.image = char.image == 255
    char.image = skeletonize(char.image)
    char.image = char.image.astype(np.uint8) * 255

    # Find contours of the skeletons
    contours, hierarchy = cv2.findContours(char.image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # Sort the contours left-to-right
    contours, _ = sort_contours(contours, "left-to-right")
    for contour in contours:
        if cv2.arcLength(contour, True) > 100:
            # Initialize mask
            mask = np.zeros(char.image.shape, np.uint8)
            # Bounding rect of the contour
            x, y, w, h = cv2.boundingRect(contour)
            mask[y:y + h, x:x + w] = 255
            # Get only the skeleton in the mask area
            mask = cv2.bitwise_and(mask, char.image)
            # Take the coordinates of the skeleton points
            rows, cols = np.where(mask == 255)
            # Add the coordinates to the list
            char.skeleton = list(zip(cols, rows))

            # Find the endpoints for the shape and update a list
            char.endpoints = skeleton_endpoints(mask)

            # Find the jointpoints for the shape and update a list
            char.jointpoints = skeleton_jointpoints(mask)

            # Draw the endpoints
            [cv2.circle(char.image, ep, 5, 255, 1) for ep in char.endpoints]
            print("Endpoints %s" % char.endpoints)
            [cv2.circle(char.image, jp, 4, 180, 1) for jp in char.jointpoints]
            print("Jointpoints %s" % char.jointpoints)

        else:
            return False
    return True


def skeleton_jointpoints(skel):
    skel = skel.copy()
    skel[skel != 0] = 1
    skel = np.uint8(skel)

    # apply the convolution
    kernel = np.uint8([[1, 3, 1],
                       [3, 10, 3],
                       [1, 3, 1]])
    src_depth = -1
    filtered = cv2.filter2D(skel, src_depth, kernel)

    # now look through to find the value greater than or equal to 17 (i.e has at least 3 neighbouring pixels,
    # and at least 2 of them are in the horizontal/vertical direction
    # this returns a mask of the jointpoints
    rows, cols = np.where(filtered >= 17)
    coords = list(zip(cols, rows))

    # Remove all jointpoints that are next to each other (i.e. distance < sqrt(2) which we say is ~ 1.5
    for point1 in coords:
        for point2 in coords:
            if point2 not in coords or point1 == point2:
                continue
            x1, y1 = point1
            x2, y2 = point2
            # Pythagoras to figure out distance
            distance = sqrt((abs(x1 - x2)) ** 2 + (abs(y1 - y2)) ** 2)
            if distance < 1.5:
                print("Joint Points %s and %s are very close (%s), removing %s" % (point1, point2, distance, point2))
                coords.remove(point2)

    return coords


def skeleton_endpoints(skel):
    skel = skel.copy()
    skel[skel != 0] = 1
    skel = np.uint8(skel)

    # apply the convolution
    kernel = np.uint8([[1, 1, 1],
                       [1, 10, 1],
                       [1, 1, 1]])
    src_depth = -1
    filtered = cv2.filter2D(skel, src_depth, kernel)

    # now look through to find the value of 11
    # this returns a mask of the endpoints
    out = np.zeros_like(skel)
    out[np.where(filtered == 11)] = 1
    rows, cols = np.where(filtered == 11)
    coords = list(zip(cols, rows))
    return coords
