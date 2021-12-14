import math
from math import pi
from customObjects import RobotStatus, Segment

DISTANCE_EPSILON = 0.15
ALMOST_ZERO = 0.06

class KobukiRobot:
    MAX_DRINK_CAPACITY = 3
    
    def __init__(self, no, graph):
        self.no = no
        self.state = RobotStatus.LOADING
        self.route = []
        self.drinks = []
        self.destinations = []
        # On the segment we are traveling down, prev_waypoint represents
        # the point we are coming from, and next_waypoint is where we are going
        self.prev_waypoint = None
        self.next_waypoint = None
        self.graph = graph
        self.home = None

    def set_home(self, waypoint):
        self.home = waypoint
        self.prev_waypoint = waypoint

    def get_status(self):
        return self.state

    def get_num_drinks(self):
        return len(self.drinks)

    def place_drink(self, drink, waypoint):
        self.destinations.append(waypoint) # Drink waypoint
        self.drinks.append(drink) # Drink name

    def push_button(self):
        if self.state == RobotStatus.UNLOADING:
            # TODO: replace drinks, destinations with Order class because this is garbage
            for (drink, dest) in zip(self.drinks, self.destinations):
                if dest is self.prev_waypoint:
                    self.destinations.remove(dest)
                    self.drinks.remove(drink)
                    #print("Bot {} delivered {}".format(self.no, drink))

            if len(self.drinks) > 0:
                self.state = RobotStatus.DELIVERYING
            else:
                self.state = RobotStatus.RETURNING
        elif self.state == RobotStatus.LOADING:
            if len(self.drinks) > 0:
                self.state = RobotStatus.DELIVERYING


    def update(self, webcam_data):
        x = webcam_data["x"]
        y = webcam_data["y"]
        heading = webcam_data["heading"]

        if self.next_waypoint is not None:
            distance_to_next = math.dist((x, y), self.next_waypoint.coords)
            if distance_to_next < DISTANCE_EPSILON:
                if self.next_waypoint in self.destinations:
                    self.state = RobotStatus.UNLOADING
                    self.prev_waypoint = self.next_waypoint
                    self.next_waypoint = None
                    self.graph.unlock_by_id(self.no)
                    self.prev_waypoint.lock_holder = self.no
                elif self.next_waypoint is self.home:
                    self.state = RobotStatus.LOADING
                    self.prev_waypoint = self.next_waypoint
                    self.next_waypoint = None
                    self.displays = self.drinks.copy()
                    self.graph.unlock_by_id(self.no)
                    self.prev_waypoint.lock_holder = self.no
                else:
                    self.prev_waypoint = self.next_waypoint

                self.displays = [] # By default, the display is blank.

        # Prep the path, even if we aren't moving yet
        # Recompute the shortest path each time, because computers are fast
        if self.state != RobotStatus.UNLOADING and self.state != RobotStatus.LOADING:
            if len(self.drinks) > 0:
                self.route = self.graph.find_route(self.prev_waypoint, [self.destinations[0]], self.no)
            else:
                self.route = self.graph.find_route(self.prev_waypoint, [self.home], self.no)

            if self.route is None:
                self.next_waypoint = None
            else:
                self.next_waypoint = self.route[1]
                #print("setting next waypoint for", self.no, ":", self.next_waypoint)

    def get_heading(self, webcam_data):
        """
        Returns the bluetooth transmission data.
        """
        self.segment = None
        if self.state == RobotStatus.LOADING or self.state == RobotStatus.UNLOADING:
            return 0, 0, 0
        elif self.next_waypoint is None:
            # We are stalled waiting for a path to clear up
            return 0, 0, 0
        else:
            this_x = webcam_data["x"]
            this_y = webcam_data["y"]
            heading = webcam_data["heading"]
            x0, y0 = self.prev_waypoint.coords
            x1, y1 = self.next_waypoint.coords
            segment = Segment(x0, y0, x1, y1)
            # expose instance variable for debugging
            self.segment = segment
            return get_error_terms(this_x, this_y, heading, segment)

def get_error_terms(x, y, heading, desired_segment):
    """Calculate and return the positional error, heading error, and 
    remaining distance.
    A positive positional error is to the right of the segment. Positive 
    heading error is to the right of desired heading.
    """
    x1 = desired_segment.x0
    y1 = desired_segment.y0
    x2 = desired_segment.xf
    y2 = desired_segment.yf

    def subtract_angles(a, b):
        """Result ranges from [-pi, pi]."""
        result = a-b
        if result > pi:
            result -= 2*pi
        elif result < -pi:
            result += 2*pi
        return result

    # Find error terms
    robot_to_endpoint = Segment(x, y, x2, y2).segment_angle()
    # If robot has passed the endpoint, turn around.
    segment_angle = desired_segment.segment_angle()
    angle_difference = subtract_angles(segment_angle, robot_to_endpoint)
    if abs(angle_difference) > pi/2:
        # Robot passed the endpoint. Aim directly for the endpoint.
        print("overshoot", desired_segment)
        heading_error = subtract_angles(heading, robot_to_endpoint)
        positional_error = 0
    else:
        heading_error = subtract_angles(heading, segment_angle)

    remaining_dist = math.dist([x, y], [x2, y2])
    segment_length = desired_segment.length_squared()**0.5
    assert(segment_length >= ALMOST_ZERO)
    positional_error = ((x2-x1)*(y1-y)-(y2-y1)*(x1-x))/segment_length

    return positional_error, heading_error, remaining_dist
