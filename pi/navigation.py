"""navigation.py
Plans the routes for each robot and keeps the robots on their track.
"""

# Project modules
from customObjects import Segment
from orderScheduler import OrderScheduler



class Navigation:
    # x y coordinates of base station
    base_station_x = None
    base_station_y = None
    def __init__(self, num_kobukis, kobuki_state):
        self.num_kobukis = num_kobukis
        self.kobuki_state = kobuki_state

    def get_error_terms(self, x, y, heading, desired_segment):
        """Calculate and return the positional error and heading error."""
        # TODO
        positional_error = 0
        heading_error = 0
        remaining_dist = 1000
        return positional_error, heading_error, remaining_dist
    
    def get_desired_segment(self, kobuki_id, order, webcam_data):
        # TODO
        state = self.kobuki_state[kobuki_id]
        if state == RobotStatus.IDLE:
            # TODO stop the motors.
            pass
        elif state == RobotStatus.GETTING_ORDER:
            # Drive the path to get the order from the base station.
            x0 = webcam_data["x"]
            y0 = webcam_data["y"]
            segment = Segment(x0, y0, self.base_station_x, self.base_station_y)
            return segment
        elif state == RobotStatus.DELIVERING_ORDER:
            # Drive the path to get the order from base station to table.

            pass
        else:
            print("navigation state not implemented")
        return segment

    def set_destination(self, kobuki_id, x, y):
        # TODO
        pass
    
    def set_base_station_location(x, y):
        self.base_station_x = x
        self.base_station_y = y
