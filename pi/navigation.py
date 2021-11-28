"""navigation.py
Plans the routes for each robot and keeps the robots on their track.
"""

# External libraries
from enum import Enum

# Project modules
from customObjects import Segment
from orderScheduler import OrderScheduler

class RobotStatus(Enum):
    IDLE = 0
    GETTING_ORDER = 1
    DELIVERING_ORDER = 2

class Navigation:
    def __init__(self, num_kobukis, scheduler):
        self.num_kobukis = num_kobukis
        self.scheduler = scheduler
        self.kobuki_state = []
        for i in range(self.num_kobukis):
            self.kobuki_state.append(RobotStatus.IDLE)

    def get_error_terms(self, x, y, heading, desired_segment):
        """Calculate and return the positional error and heading error."""
        positional_error = 0
        heading_error = 0
        return positional_error, heading_error
    
    def get_desired_segment(self, kobuki_id):
        # TODO
        state = self.kobuki_state[kobuki_id]
        if state == RobotStatus.IDLE:
            order = self.scheduler.get_next_order()
            if order is not None:
                print("Scheduled order number", order.order_id)
                # Get the next order and calculate the desired path.
        elif state == RobotStatus.GETTING_ORDER:
            # Drive the path to get the order from the base station.
            pass
        elif state == RobotStatus.DELIVERING_ORDER:
            # Drive the path to get the order from the base station.
            pass
        else:
            print("navigation state not implemented")
        segment = Segment()
        return segment

    def set_destination(self, kobuki_id, x, y):
        # TODO
        pass
