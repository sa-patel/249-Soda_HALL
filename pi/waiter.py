import math
from math import pi
from customObjects import RobotStatus, Segment

DISTANCE_EPSILON = 0.15
ALMOST_ZERO = 0.06

class KobukiRobot:
    MAX_DRINK_CAPACITY = 3
    
    def __init__(self, id, graph):
        self.id = id
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
            self.destinations.pop(0) # TODO this will not work for unordered deliveries.
            drink_name = self.drinks.pop(0)
            print("Bot {} delivered {}".format(self.id, drink_name))

        if len(self.drinks) > 0 and len(self.destinations) > 0:
            route = self.graph.find_route(self.prev_waypoint, [self.destinations[0]])
            if len(route) >= 2:
                self.next_waypoint = route[1]
            else:
                self.next_waypoint = None
                return # Early return to avoid state update
        else:
            route = self.graph.find_route(self.prev_waypoint, [self.home])
            if len(route) >= 2:
                self.next_waypoint = route[1]
            else:
                self.next_waypoint = None
                return # Already home.

        self.state = RobotStatus.MOVING


    def update(self, webcam_data):
        x = webcam_data["x"]
        y = webcam_data["y"]
        heading = webcam_data["heading"]

        if self.next_waypoint is not None and math.dist((x, y), self.next_waypoint.coords) < DISTANCE_EPSILON:
            self.displays = [] # By default, the display is blank.
            if self.next_waypoint in self.destinations:
                self.state = RobotStatus.UNLOADING
                self.prev_waypoint = self.next_waypoint
            elif self.next_waypoint is self.home:
                self.state = RobotStatus.LOADING
                self.prev_waypoint = self.next_waypoint
                self.next_waypoint = None
                self.displays = self.drinks.copy()
            else:
                # TODO: unlock next waypoint
                self.prev_waypoint = self.next_waypoint
                # Recompute the shortest path each time, because computers are fast
                if len(self.destinations) > 0:
                    route = self.graph.find_route(self.prev_waypoint, [self.destinations[0]])
                else:
                    route = self.graph.find_route(self.prev_waypoint, [self.home])
                if len(route) >= 2:
                    self.next_waypoint = route[1]
                else:
                    self.next_waypoint = None

    def get_heading(self, webcam_data):
        """
        Returns the bluetooth transmission data.
        """
        self.segment = None
        if self.state == RobotStatus.LOADING or self.state == RobotStatus.UNLOADING:
            return 0, 0, 0
        elif self.next_waypoint is None:
            return 0, 0, 0
        else:
            this_x = webcam_data["x"]
            this_y = webcam_data["y"]
            heading = webcam_data["heading"]
            x0, y0 = self.prev_waypoint.coords
            x1, y1 = self.next_waypoint.coords
            segment = Segment(x0, y0, x1, y1)
            self.segment = segment # expose instance variable for debugging

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
