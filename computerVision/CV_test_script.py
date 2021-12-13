from CV_positioning_system import CV_positioning_system
import time

test_obj = CV_positioning_system()
test_obj.get_stationary_positions()

while True:

	test_obj.get_robot_positions()
	time.sleep(5)