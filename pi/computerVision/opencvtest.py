import cv2
class Webcam_test(): 

    def determine_port(self):
        for i in range(40): 
            port_num = i
            cam = cv2.VideoCapture(i)
            ret, image = cam.read()
            if ret: 
                break

        cam.release()
        cv2.destroyAllWindows()
        return port_num

		# try cam = cv2.VideoCapture(0): 
		# 	self.port_num = 0
		# except:
		# 	self.port_num = 1
		# 	cam = cv2.VideoCapture(self.port_num)

#cv2.imwrite('/home/pi/testimage.jpg', image)

