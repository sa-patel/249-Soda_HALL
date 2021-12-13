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
rightImages = glob.glob('/Users/tigre/pongBot/rightCamStereoCal/*.png')

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

for fname in rightImages:
    img = cv.imread(fname)
    grayR = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(grayR, (7,7), None)
    # If found, add object points, image points (after refining them)
    print(ret)
    if ret == True:
        objpointsR.append(objp)
        corners2 = cv.cornerSubPix(grayR,corners, (11,11), (-1,-1), criteria)
        imgpointsR.append(corners)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (7,7), corners2, ret)
        cv.imshow('img', img)
        # cv.waitKey(500)
cv.destroyAllWindows()

retR, mtxR, distR, rvecsR, tvecsR = cv.calibrateCamera(objpointsR, imgpointsR, grayR.shape[::-1], None, None)
hR,wR= img.shape[:2]
new_mtxR, roiR= cv.getOptimalNewCameraMatrix(mtxR,distR,(wR,hR),1,(wR,hR))


# Stereo Cam Calibration
flags = 0
flags |= cv.CALIB_FIX_INTRINSIC
# Here we fix the intrinsic camara matrixes so that only Rot, Trns, Emat and Fmat are calculated.
# Hence intrinsic parameters are the same 

criteria_stereo= (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# This step is performed to transformation between the two cameras and calculate Essential and Fundamenatl matrix
retS, new_mtxL, distL, new_mtxR, distR, Rot, Trns, Emat, Fmat = cv.stereoCalibrate(objpointsR, imgpointsL, imgpointsR, new_mtxL, distL, new_mtxR, distR, grayL.shape[::-1], criteria_stereo, flags)


# Stereo Rectification
rectify_scale = 1
rect_l, rect_r, proj_mat_l, proj_mat_r, Q, roiL, roiR= cv.stereoRectify(new_mtxL, distL, new_mtxR, distR, grayL.shape[::-1], Rot, Trns, rectify_scale,(0,0))


# Find the undistorted and rectified stereo pairs
Left_Stereo_Map= cv.initUndistortRectifyMap(new_mtxL, distL, rect_l, proj_mat_l,
                                             grayL.shape[::-1], cv.CV_16SC2)
Right_Stereo_Map= cv.initUndistortRectifyMap(new_mtxR, distR, rect_r, proj_mat_r,
                                              grayR.shape[::-1], cv.CV_16SC2)

print("Saving parameters ......")
cv_file = cv.FileStorage("improved_params2.xml", cv.FILE_STORAGE_WRITE)
cv_file.write("Left_Stereo_Map_x",Left_Stereo_Map[0])
cv_file.write("Left_Stereo_Map_y",Left_Stereo_Map[1])
cv_file.write("Right_Stereo_Map_x",Right_Stereo_Map[0])
cv_file.write("Right_Stereo_Map_y",Right_Stereo_Map[1])
cv_file.release()
