# Camera Matrix calibration, referenced OpenCV.org - Camera Calibration page
# Imput: pre-captured images from left and right cameras
# Output: Camera Matrix
import numpy as np
import cv2 as cv
import glob

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((7*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:7].T.reshape(-1,2)
# Arrays to store object points and image points from all the images.
objpointsL = [] # 3d point in real world space
imgpointsL = [] # 2d points in image plane.

objpointsR = [] # 3d point in real world space
imgpointsR = [] # 2d points in image plane.

leftImages = glob.glob('/Users/tigre/pongBot/leftCamStereoCal/*.png')

# Individual Camera Calibration
for fname in leftImages:
    img = cv.imread(fname)
    grayL = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(grayL, (7,7), None)
    # If found, add object points, image points (after refining them)
    print(ret)
    if ret == True:
        objpointsL.append(objp)
        corners2 = cv.cornerSubPix(grayL,corners, (11,11), (-1,-1), criteria)
        imgpointsL.append(corners)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (7,7), corners2, ret)
        cv.imshow('img', img)
        # cv.waitKey(500)
cv.destroyAllWindows()

retL, mtxL, distL, rvecsL, tvecsL = cv.calibrateCamera(objpointsL, imgpointsL, grayL.shape[::-1], None, None)
hL,wL= img.shape[:2]
new_mtxL, roiL= cv.getOptimalNewCameraMatrix(mtxL,distL,(wL,hL),1,(wL,hL))



# Draws from https://mecaruco2.readthedocs.io/en/latest/notebooks_rst/Aruco/aruco_basics.html
import numpy as np
import cv2, PIL
from cv2 import aruco
import matplotlib.pyplot as plt
import matplotlib as mpl

# Show a frame
frame = cv2.imread("AR_Tag.png")

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
parameters =  aruco.DetectorParameters_create()
corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)

plt.figure()
plt.imshow(frame_markers)
for i in range(len(ids)):
    c = corners[i][0]
    plt.plot([c[:, 0].mean()], [c[:, 1].mean()], "o", label = "id={0}".format(ids[i]))
plt.legend()
plt.show()

size_of_marker =  0.0145 # side lenght of the marker in meter
rvecs,tvecs, trash = aruco.estimatePoseSingleMarkers(corners, size_of_marker , new_mtxL, distL)

length_of_axis = 0.01
imaxis = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
for i in range(len(tvecs)):
    imaxis = aruco.drawAxis(imaxis, new_mtxL, distL, rvecs[i], tvecs[i], length_of_axis)

print('dist:', distL)
plt.figure()
plt.imshow(imaxis)
plt.show()