# AR Tag Relative pose code and test,
# Author: S. Patel, 12/4/2021
# referenced OpenCV.org - Camera Calibration page
# Imput: pre-captured images from left and right cameras
# Output: Camera Matrix
# Draws from OpenCV Camera Calibration guide
# Draws from https://mecaruco2.readthedocs.io/en/latest/notebooks_rst/Aruco/aruco_basics.html
# Draws from https://aliyasineser.medium.com/calculation-relative-positions-of-aruco-markers-eee9cc4036e3 
# General flow:
# Find position of origin and other stationary AR Tag markers
# Save positional data and remove markers if necessary
from computerVision.opencvtest import Webcam_test
import numpy as np
import cv2 as cv
import glob
import cv2, PIL
from cv2 import aruco
import matplotlib.pyplot as plt
import matplotlib as mpl
import math


origin_id = 99; # The origin of the space defined by an AR Tag

# Camera Calibration section
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

calibImages = glob.glob('computerVision/rightCamCalPics/*.png')

# Individual Camera Calibration
for fname in calibImages:
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
origin_tvec = np.empty([3,1])
origin_rvec = np.empty([3,1])

# ID 100 is origin. All results are provided relative to this origin coordinate frame 
# The stationary positions reflect physical positions of waypoints and destination points. 
# These do not move over time.
# The robot positions return the positions and headings of the robots
# Robots are designated AR Tag IDs 98 & 99
class CV_positioning_system:
	port_num = 0
	cam = 0
	# The stationary positions reflect physical positions of waypoints and destination points. 
	# These do not move over time.

	def get_stationary_positions(self):
		"""Get locations of tables and waypoints"""
		global origin_rvec
		global origin_tvec
		# -------------------------------------------------------------
		# Test AR_Tag Relative pose with a fixed image. This section of code will be suplanted with live video later on
		# Test image shows a robot (ID 2) pointed towards destination (ID 3). Origin marker is given by ID 1

		# Two options to get static images, 1. live video feed and capture, or 2. still image 
		# Single image test portion
		# frame = cv.imread("orient2.png")
		# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		# aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)
		# parameters =  aruco.DetectorParameters_create()
		# corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
		# frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
		

		# Live video

		# for i in range(4): 
		# 	try: 
		# 		self.port_num = i
		# 		cam = cv2.VideoCapture(i)
		# 		ret, image = cam.read()
		# 		cv2.imshow('Imagetest',image)
		# 		break
		# 	except:
		# 		pass


		# for i in range(): 
		# 	self.port_num = i
		# 	cam = cv2.VideoCapture(i)
		# 	ret, image = cam.read()
		# 	if ret: 
		# 		break

		# print(self.port_num)
		
		# for i in range(5): 
		# 	self.port_num = i
		# 	cam = cv2.VideoCapture(i)
		# 	ret, image = cam.read()
		# 	if ret: 
		# 		break
		webcam_testing = Webcam_test()
		self.port_num = webcam_testing.determine_port()
		print(self.port_num)
		# try:
		# 	cam = cv2.VideoCapture(0) 
		# 	self.port_num = 0
		# 	ret, image = cam.read()
		# 	cv2.imshow('Imagetest',image)
		# except:
		# 	try:
		# 		self.port_num = 1
		# 		cam = cv2.VideoCapture(self.port_num)
		# 		ret, image = cam.read()
		# 		cv2.imshow('Imagetest',image)
		# 	except:
		# 		self.port_num = 2
		# 		cam = cv2.VideoCapture(self.port_num)
		# 		ret, image = cam.read()
		# 		cv2.imshow('Imagetest',image)
		
		# self.port_num = 2
		self.cam = cv2.VideoCapture(self.port_num)
		ret, frame = self.cam.read()

		cv2.namedWindow("test")

		image_accepted = False

		while not (image_accepted):
			ret, frame = self.cam.read()
			if not ret:
				print("Camera Read failure")
				break

			# Show a frame
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			# Choose AR Tag Dictionary size
			aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)
			parameters =  aruco.DetectorParameters_create()
			corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
			frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)

			if (ids) is not None:
				for i in range(len(ids)):
					c = corners[i][0]
					plt.plot([c[:, 0].mean()], [c[:, 1].mean()], "o", label = "id={0}".format(ids[i]))

				size_of_marker =  0.18415 # side lenght of the marker in meter
				rvecs,tvecs, trash = aruco.estimatePoseSingleMarkers(corners, size_of_marker , new_mtxL, distL)

				length_of_axis = 0.1
				imaxis = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
				for i in range(len(tvecs)):
					imaxis = aruco.drawAxis(imaxis, new_mtxL, distL, rvecs[i], tvecs[i], length_of_axis)
					#print("Tvec: ", tvecs[i])
					#print("rvec: ", rvecs[i])
					print('AR_Tag Found')
					cv2.imshow('AR_Tag', imaxis)


			k = cv2.waitKey(1)
			if k%256 == 32:
				# self.cam.release()
				cv2.destroyAllWindows()
				image_accepted = True

			if k%256 == 27:
				# ESC pressed
				print("Escape hit, closing...")
				# self.cam.release()
				cv2.destroyAllWindows()
				break
				
		# Iterate through the IDs and find their relative positions in the origin frame coordinates
		if ids is not None:
			for i in range(len(ids)):
				c = corners[i][0]
				plt.plot([c[:, 0].mean()], [c[:, 1].mean()], "o", label = "id={0}".format(ids[i]))

			size_of_marker =  0.18415 # Length of AR Tag side (in meters)
			rvecs,tvecs, trash = aruco.estimatePoseSingleMarkers(corners, size_of_marker , new_mtxL, distL)

			length_of_axis = 0.1
			imaxis = aruco.drawDetectedMarkers(frame.copy(), corners, ids)

			for i in range(len(tvecs)):
				#print("id: {0} ".format(ids[i]))
				imaxis = aruco.drawAxis(imaxis, new_mtxL, distL, rvecs[i], tvecs[i], length_of_axis)
				# print("tvec: {0} ".format(ids[i]), tvecs[i])
				# print("rvec: {0} ".format(ids[i]), rvecs[i])

				if (ids[i] == origin_id):
					print("Origin found")
					origin_tvec = tvecs[i]
					origin_rvec = rvecs[i]
					R_origin, _ = cv2.Rodrigues(origin_rvec)

			id_positions = {}
			if (origin_tvec is not None):
				for i in range(len(tvecs)):
					# print("tvec: {0} ".format(ids[i]), tvecs[i])
					# print("rvec: {0} ".format(ids[i]), rvecs[i])

					# print("Position of ID {0} in Origin coordinates".format(ids[i]))
					composedRvec, composedTvec = relativePosition(rvecs[i], tvecs[i], origin_rvec, origin_tvec)
					# print("composedTvec: {0} ".format(ids[i]), composedTvec)
					# print("composedRvec: {0} ".format(ids[i]), composedRvec)

					composedRvecMatrix, _ = cv2.Rodrigues(composedRvec)
					# print("composedRvec Matrix: \n", composedRvecMatrix)
					# print("composedRvec x axis[:,0]", composedRvecMatrix[:,0])
					# print("composedRvec y axis[:,1]", composedRvecMatrix[:,1])

					R_target, _ = cv2.Rodrigues(rvecs[i]) # get the Rotation matrix
					# print("R_target: ", R_target)
					# print("R_target[:,0]: id {0} ".format(ids[i]), R_target[:,0])
					# print("R_target[:,1]: id {0} ".format(ids[i]), R_target[:,1])
					# print("R_origin[:,0]:", R_origin[:,0])


					# takes the x axis (the first column of the rotation matrix) and finds the relative angle between them using arc-cosine
					relative_angle = (360/ (2*np.pi)) * np.arccos(np.dot(R_origin[:,0], R_target[:,0]))

					# Take the dot product of the robot x-axis with the origin y-axis to recover the angle that was lost from arc-cosine
					# If the dot product is negative, the angle will be in the opposite direction
					if (np.dot(R_origin[:,1], R_target[:,0]) < 0):
						relative_angle = -relative_angle
					
					# print("rel angle:", relative_angle)
					# print("rvec_origin Z axis angle", (360/(2*np.pi)) * composedRvec[2])

					id_positions[int(ids[i])] = (float(composedTvec[0]), float(composedTvec[1]), relative_angle)
					print('----------------')

		# plt.figure()
		# plt.imshow(imaxis)
		# plt.show()

		# print(id_positions)
		return id_positions

	# Provides robot positions return the positions and headings of the robots
	# Robots are designated AR Tag IDs 98 & 99
	def get_robot_positions(self):
		"""Get location and heading of kobukis"""
		global origin_rvec
		global origin_tvec

		robot1_ID = 97
		robot2_ID = 98

		# cam = cv2.VideoCapture(self.port_num)
		ret, frame = self.cam.read()

		# cv2.namedWindow("test")

		ret, frame = self.cam.read()
		if not ret:
			print("Camera Read failure")

		# cam.release()
		# cv2.destroyAllWindows()

		# Show a frame
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		# Choose AR Tag Dictionary size
		aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)
		parameters =  aruco.DetectorParameters_create()
		corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
		frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)

		if (ids) is not None:
			for i in range(len(ids)):
				c = corners[i][0]
				plt.plot([c[:, 0].mean()], [c[:, 1].mean()], "o", label = "id={0}".format(ids[i]))

			size_of_marker =  0.18415 # side lenght of the marker in meter
			rvecs,tvecs, trash = aruco.estimatePoseSingleMarkers(corners, size_of_marker , new_mtxL, distL)

			length_of_axis = 0.1
			imaxis = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
			for i in range(len(tvecs)):
				imaxis = aruco.drawAxis(imaxis, new_mtxL, distL, rvecs[i], tvecs[i], length_of_axis)
				#print("Tvec: ", tvecs[i])
				#print("rvec: ", rvecs[i])
				#print('AR_Tag Found')

		# Iterate through the IDs and find their relative positions in the origin frame coordinates
		if ids is not None:
			for i in range(len(ids)):
				c = corners[i][0]
				plt.plot([c[:, 0].mean()], [c[:, 1].mean()], "o", label = "id={0}".format(ids[i]))

			size_of_marker =  0.18415 # Length of AR Tag side (in meters)
			rvecs,tvecs, trash = aruco.estimatePoseSingleMarkers(corners, size_of_marker , new_mtxL, distL)

			length_of_axis = 0.1
			imaxis = aruco.drawDetectedMarkers(frame.copy(), corners, ids)

			for i in range(len(tvecs)):
				#print("id: {0} ".format(ids[i]))
				imaxis = aruco.drawAxis(imaxis, new_mtxL, distL, rvecs[i], tvecs[i], length_of_axis)
				# print("tvec: {0} ".format(ids[i]), tvecs[i])
				# print("rvec: {0} ".format(ids[i]), rvecs[i])

				if (ids[i] == origin_id):
					# print("Origin found")
					origin_tvec = tvecs[i]
					origin_rvec = rvecs[i]
					R_origin, _ = cv2.Rodrigues(origin_rvec)

		robot_positions = {}
		# Iterate through the IDs and find their relative positions in the origin frame coordinates
		if ids is not None:
			size_of_marker =  0.18415 # Length of AR Tag side (in meters)
			rvecs,tvecs, trash = aruco.estimatePoseSingleMarkers(corners, size_of_marker , new_mtxL, distL)

			length_of_axis = 0.1
			imaxis = aruco.drawDetectedMarkers(frame.copy(), corners, ids)

			R_origin, _ = cv2.Rodrigues(origin_rvec)

			if (origin_tvec is not None):
				for i in range(len(ids)):
					if (ids[i] == robot1_ID) or (ids[i] == robot2_ID): 
						# print("tvec: {0} ".format(ids[i]), tvecs[i])
						# print("rvec: {0} ".format(ids[i]), rvecs[i])

						#print("Position of ID {0} in Origin coordinates".format(ids[i]))
						composedRvec, composedTvec = relativePosition(rvecs[i], tvecs[i], origin_rvec, origin_tvec)
						#print("composedTvec: {0} ".format(ids[i]), composedTvec)
						#print("composedRvec: {0} ".format(ids[i]), composedRvec)

						composedRvecMatrix, _ = cv2.Rodrigues(composedRvec)
						#print("composedRvec Matrix: \n", composedRvecMatrix)
						# print("composedRvec x axis[:,0]", composedRvecMatrix[:,0])
						# print("composedRvec y axis[:,1]", composedRvecMatrix[:,1])

						R_target, _ = cv2.Rodrigues(rvecs[i]) # get the Rotation matrix
						#print("R_target: ", R_target)
						# print("R_target[:,0]: id {0} ".format(ids[i]), R_target[:,0])
						# print("R_target[:,1]: id {0} ".format(ids[i]), R_target[:,1])
						# print("R_origin[:,0]:", R_origin[:,0])


						# takes the x axis (the first column of the rotation matrix) and finds the relative angle between them using arc-cosine
						relative_angle = (360/ (2*np.pi)) * np.arccos(np.dot(R_origin[:,0], R_target[:,0]))

						# Take the dot product of the robot x-axis with the origin y-axis to recover the angle that was lost from arc-cosine
						# If the dot product is negative, the angle will be in the opposite direction
						if (np.dot(R_origin[:,1], R_target[:,0]) < 0):
							relative_angle = -relative_angle
						
						#print("rel angle:", relative_angle)
						#print("rvec_origin Z axis angle", (360/(2*np.pi)) * composedRvec[2])

						robot_positions[int(ids[i])] = (float(composedTvec[0]), float(composedTvec[1]), -math.radians(relative_angle))
						#print('----------------')
		#print(robot_positions)
		return robot_positions


def inversePerspective(rvec, tvec):
	R, _ = cv2.Rodrigues(rvec)
	R = np.matrix(R).T
	invTvec = np.dot(-R, np.matrix(tvec))
	invRvec, _ = cv2.Rodrigues(R)
	return invRvec, invTvec


def relativePosition(rvec1, tvec1, rvec2, tvec2):
	rvec1, tvec1 = rvec1.reshape((3, 1)), tvec1.reshape(
		(3, 1))
	rvec2, tvec2 = rvec2.reshape((3, 1)), tvec2.reshape((3, 1))

	# Inverse the second marker, the right one in the image
	invRvec, invTvec = inversePerspective(rvec2, tvec2)

	orgRvec, orgTvec = inversePerspective(invRvec, invTvec)
	# print("rvec: ", rvec2, "tvec: ", tvec2, "\n and \n", orgRvec, orgTvec)

	info = cv2.composeRT(rvec1, tvec1, invRvec, invTvec)
	composedRvec, composedTvec = info[0], info[1]

	composedRvec = composedRvec.reshape((3, 1))
	composedTvec = composedTvec.reshape((3, 1))
	return composedRvec, composedTvec


def draw(img, corners, imgpts):
	imgpts = np.int32(imgpts).reshape(-1,2)
	# draw ground floor in green
	# img = cv2.drawContours(img, [imgpts[:4]],-1,(0,255,0),-3)
	# draw pillars in blue color
	for i,j in zip(range(4),range(4)):
		img = cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]),(255),3)
	# draw top layer in red color
	return img

def saveCoefficients(mtx, dist):
    cv_file = cv2.FileStorage("calib_images/calibrationCoefficients.yaml", cv2.FILE_STORAGE_WRITE)
    cv_file.write("camera_matrix", mtx)
    cv_file.write("dist_coeff", dist)
    cv_file.release()


def loadCoefficients():
    # FILE_STORAGE_READ
    cv_file = cv2.FileStorage("calib_images/calibrationCoefficients.yaml", cv2.FILE_STORAGE_READ)

    # note we also have to specify the type to retrieve other wise we only get a
    # FileNode object back instead of a matrix
    camera_matrix = cv_file.getNode("camera_matrix").mat()
    dist_matrix = cv_file.getNode("dist_coeff").mat()

    # Debug: print the values
    # print("camera_matrix : ", camera_matrix.tolist())
    # print("dist_matrix : ", dist_matrix.tolist())

    cv_file.release()
    return [camera_matrix, dist_matrix]

def track(matrix_coefficients, distortion_coefficients):
	pointCircle = (0, 0)
	markerTvecList = []
	markerRvecList = []
	composedRvec, composedTvec = None, None
	while True:
		ret, frame = cap.read()
		# operations on the frame come here
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Change grayscale
		aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)  # Use 5x5 dictionary to find markers
		parameters = aruco.DetectorParameters_create()  # Marker detection parameters

		# lists of ids and the corners beloning to each id
		corners, ids, rejected_img_points = aruco.detectMarkers(gray, aruco_dict,
																parameters=parameters,
																cameraMatrix=matrix_coefficients,
																distCoeff=distortion_coefficients)

		if np.all(ids is not None):  # If there are markers found by detector
			del markerTvecList[:]
			del markerRvecList[:]
			zipped = zip(ids, corners)
			ids, corners = zip(*(sorted(zipped)))
			axis = np.float32([[-0.01, -0.01, 0], [-0.01, 0.01, 0], [0.01, -0.01, 0], [0.01, 0.01, 0]]).reshape(-1, 3)
			for i in range(0, len(ids)):  # Iterate in markers
				# Estimate pose of each marker and return the values rvec and tvec---different from camera coefficients
				rvec, tvec, markerPoints = aruco.estimatePoseSingleMarkers(corners[i], 0.02, matrix_coefficients,
																		   distortion_coefficients)

				if ids[i] == firstMarkerID:
					firstRvec = rvec
					firstTvec = tvec
					isFirstMarkerCalibrated = True
					firstMarkerCorners = corners[i]
				elif ids[i] == secondMarkerID:
					secondRvec = rvec
					secondTvec = tvec
					isSecondMarkerCalibrated = True
					secondMarkerCorners = corners[i]

				# print(markerPoints)
				(rvec - tvec).any()  # get rid of that nasty numpy value array error
				markerRvecList.append(rvec)
				markerTvecList.append(tvec)

				aruco.drawDetectedMarkers(frame, corners)  # Draw A square around the markers

			if len(ids) > 1 and composedRvec is not None and composedTvec is not None:
				info = cv2.composeRT(composedRvec, composedTvec, secondRvec.T, secondTvec.T)
				TcomposedRvec, TcomposedTvec = info[0], info[1]

				objectPositions = np.array([(0, 0, 0)], dtype=np.float)  # 3D point for projection
				imgpts, jac = cv2.projectPoints(axis, TcomposedRvec, TcomposedTvec, matrix_coefficients,
												distortion_coefficients)

				# frame = draw(frame, corners[0], imgpts)
				aruco.drawAxis(frame, matrix_coefficients, distortion_coefficients, TcomposedRvec, TcomposedTvec,
							   0.01)  # Draw Axis
				relativePoint = (int(imgpts[0][0][0]), int(imgpts[0][0][1]))
				cv2.circle(frame, relativePoint, 2, (255, 255, 0))



		# Display the resulting frame
		cv2.imshow('frame', frame)
		# Wait 3 milisecoonds for an interaction. Check the key and do the corresponding job.
		key = cv2.waitKey(3) & 0xFF
		if key == ord('q'):  # Quit
			break
		elif key == ord('c'):  # Calibration
			if len(ids) > 1:  # If there are two markers, reverse the second and get the difference
				firstRvec, firstTvec = firstRvec.reshape((3, 1)), firstTvec.reshape((3, 1))
				secondRvec, secondTvec = secondRvec.reshape((3, 1)), secondTvec.reshape((3, 1))

				composedRvec, composedTvec = relativePosition(firstRvec, firstTvec, secondRvec, secondTvec)


# Checks if a matrix is a valid rotation matrix.
def isRotationMatrix(R) :
	Rt = np.transpose(R)
	shouldBeIdentity = np.dot(Rt, R)
	I = np.identity(3, dtype = R.dtype)
	n = np.linalg.norm(I - shouldBeIdentity)
	return n < 1e-6

# Calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order
# of the euler angles ( x and z are swapped ).
def rotationMatrixToEulerAngles(R) :
	assert(isRotationMatrix(R))

	sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])

	singular = sy < 1e-6

	if  not singular :
		x = math.atan2(R[2,1] , R[2,2])
		y = math.atan2(-R[2,0], sy)
		z = math.atan2(R[1,0], R[0,0])
	else :
		x = math.atan2(-R[1,2], R[1,1])
		y = math.atan2(-R[2,0], sy)
		z = 0

	return np.array([x, y, z])