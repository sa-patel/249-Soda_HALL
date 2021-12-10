"""navigation.py
Plans the routes for each robot and keeps the robots on their track.
"""

"""waypoints:
     1       2    9   10    3       4
     _________              _________
    |         |            |         |
    |_________|            |_________|
     5        6   11  12    7        8

                    0

    seat / table numbers:

      table 0                table 1
     _________              _________
    |0       1|            |4       5|
    |2_______3|            |6_______7|
"""
# External libraries
from math import pi

# Project modules
from customObjects import Segment, RobotStatus, Waypoint


norm_sq = lambda x, y: x**2 + y**2

class Graph:
    def __init__(self, n):
        self.adj = [set([]) for _ in range(n)]
    def add_edge(self, a, b):
        self.adj[a].add(b)
        self.adj[b].add(a)
    def bfs_route(self, a, b):
        """Find route of waypoints from a to b."""
        visited = [a]
        queue = [(a, [])]
        while queue:
            visit, history = queue.pop(0)
            if visit == b:
                return history+[b]
            for i in self.adj[visit]:
                if i not in visited:
                    visited.append(i)
                    queue.append((i, history+[visit]))
        return None # No route found
class Navigation:
    all_edges = (
        (0, 11),
        (11, 9),
        (0, 12),
        (12, 10),
        (11, 6),
        (6, 5),
        (12, 7),
        (7, 8),
        (10, 9),
        (11, 12),
        (9, 2),
        (2, 1),
        (10, 3),
        (3, 4)
    )
    waypoint_locations = [
        # Index is waypoint id. Value is (x,y) tuple.
        # TODO fill this in once environment is defined.
    ]
    seat_to_waypoint = [ # Index is seat number. Value is waypoint id.
        1, 2, 5, 6, 3, 4, 7, 8
    ]

    # Constants
    NUM_WAYPOINTS = 13
    DISTANCE_EPSILON = 0.15**2 # meters squared
    ALMOST_ZERO = 0.06**2
    def __init__(self, num_kobukis, kobuki_state, waypoint_locations = None):
        assert(len(kobuki_state) >= num_kobukis)
        self.num_kobukis = num_kobukis
        self.kobuki_state = kobuki_state
        self.route = [[] for _ in range(self.num_kobukis)] # List of upcoming waypoints
        self.current_segment = [None for _ in range(self.num_kobukis)]

        # Build the navigation graph
        self.graph = Graph(self.NUM_WAYPOINTS)
        for a, b in self.all_edges:
            self.graph.add_edge(a, b)

        if waypoint_locations is not None:
            self.waypoint_locations = waypoint_locations

    def get_error_terms(self, x, y, heading, desired_segment):
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
            
            # Find distance from robot to the segment.
            segment_length = desired_segment.length_squared()**0.5
            if segment_length < self.ALMOST_ZERO:
                print("Error: segment length near zero")
            positional_error = ((x2-x1)*(y1-y)-(y2-y1)*(x1-x))/segment_length
        
        remaining_dist = norm_sq(x2-x, y2-y)**0.5

        return positional_error, heading_error, remaining_dist
    
    def advance_current_segment(self, kobuki_id):
        """Generate the next segment from self.route."""
        # Return False if route is completed.
        # TODO indicate if segment is finished so the robot can stop, turn in place, and continue.
        route = self.route[kobuki_id-1]
        if len(route) < 2:
            return False

        point_a = route.pop(0)
        point_b = route[0]
        s = self.convert_waypoints_to_segment(point_a, point_b)
        # Ignore this segment if length is small
        if s.length_squared() < self.ALMOST_ZERO:
            return self.advance_current_segment(kobuki_id)
        else:
            self.current_segment[kobuki_id-1] = s
        return True

    def point_reached(self, x, y, x2, y2):
        """Returns true if the points are within epsilon distance of each other"""
        dist_sq = norm_sq(x - x2, y - y2)
        return dist_sq < self.DISTANCE_EPSILON
    
    def get_desired_segment(self, kobuki_id, webcam_data):
        assert(0 < kobuki_id and kobuki_id <= self.num_kobukis)
        current_segment = self.current_segment[kobuki_id-1]
        def advance_segment_check_state(done_state):
            # Get the next segment
            segments_remain = self.advance_current_segment(kobuki_id)
            if not segments_remain:
                self.kobuki_state[kobuki_id-1] = [done_state, order, num_drinks]
                return None
            return self.current_segment[kobuki_id-1]

        state, order, num_drinks = self.kobuki_state[kobuki_id-1]
        if state == RobotStatus.IDLE:
            # stop the motors.
            return None
        elif state == RobotStatus.UNLOADING:
            # stop the motors.
            return None
        elif state == RobotStatus.LOADING:
            return None
        elif state == RobotStatus.PLAN_PATH_TO_BASE:
            # Plan the route to the base station.
            self.route[kobuki_id-1] = [] # Clear any saved route
            x0 = webcam_data["x"]
            y0 = webcam_data["y"]
            self.plan_path(kobuki_id, x0, y0, 0) # Point 0 is base station.
            self.kobuki_state[kobuki_id-1] = [RobotStatus.RETURNING, order, num_drinks]
            return advance_segment_check_state(RobotStatus.IDLE)
        elif state == RobotStatus.RETURNING:
            # Drive the path to get the order from the base station.
            if current_segment is None:
                return advance_segment_check_state(RobotStatus.IDLE)
            else:
                # Determine the current segment.
                x0 = webcam_data["x"]
                y0 = webcam_data["y"]
                xf = current_segment.xf
                yf = current_segment.yf
                if self.point_reached(x0, y0, xf, yf):
                    return advance_segment_check_state(RobotStatus.IDLE)
                return current_segment
        elif state == RobotStatus.PLAN_PATH_TO_TABLE:
            self.route[kobuki_id-1] = [] # Clear any saved routes
            x0 = webcam_data["x"]
            y0 = webcam_data["y"]
            dest = self.convert_seat_to_waypoint(order.pop(0).seat)
            self.plan_path(kobuki_id, x0, y0, dest) # Point 0 is base station.
            self.kobuki_state[kobuki_id-1] = [RobotStatus.DELIVERING_ORDER, order, num_drinks]
            return advance_segment_check_state(RobotStatus.UNLOADING)
        elif state == RobotStatus.DELIVERING_ORDER:
            # Drive the path to get the order to the seat.
            if current_segment is None:
                return advance_segment_check_state(RobotStatus.UNLOADING)
            else:
                # Determine the current segment.
                x0 = webcam_data["x"]
                y0 = webcam_data["y"]
                xf = current_segment.xf
                yf = current_segment.yf
                if self.point_reached(x0, y0, xf, yf):
                    return advance_segment_check_state(RobotStatus.UNLOADING)
                return current_segment
        else:
            print("navigation state {} not implemented", state)
        return None

    def plan_path(self, kobuki_id, x0, y0, destination):
        start = Waypoint("XY", (x0, y0))
        route = self.route[kobuki_id-1]
        route.append(start)

        # Find the nearest defined waypoint.
        nearest = self.nearest_waypoint(x0, y0)

        # Make route to destination
        plan_route = self.graph.bfs_route(nearest, destination)
        if plan_route is not None:
            # Convert ints to Waypoints
            waypoint_route = [Waypoint("PREDEFINED", i) for i in plan_route]
            route += waypoint_route
            self.route_print(kobuki_id)
        else:
            print("No route found")
            route = []
    
    def nearest_waypoint(self, x0, y0):
        # find the waypoint nearest the given coordinates
        # Currently ignores obstacles and simply finds the minimum distance
        min_dist_sq = 10000
        nearest = -1
        for i in range(len(self.waypoint_locations)):
            x, y = self.waypoint_locations[i]
            dist_sq = norm_sq(x - x0, y - y0)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = i
        return nearest
    
    def convert_waypoints_to_segment(self, a, b):
        """Take 2 waypoints and create a Segment"""
        def waypoint_to_coordinate(p):
            if p.type == "PREDEFINED":
                x, y = self.lookup_waypoint(p.value)
            elif p.type == "XY":
                x, y = p.value
            return x, y
        xa, ya = waypoint_to_coordinate(a)
        xb, yb = waypoint_to_coordinate(b)
        s = Segment(xa, ya, xb, yb)
        return s
        
    def lookup_waypoint(self, p):
        """Find coordinates of waypoint given by its id"""
        return self.waypoint_locations[p]
    
    def convert_seat_to_waypoint(self, seat):
        """Convert seat number to waypoint number"""
        return self.seat_to_waypoint[seat]
    
    def route_print(self, kobuki_id):
        """Testing function to print the route"""
        print("route kobuki", kobuki_id, end=" ")
        route = self.route[kobuki_id-1]
        for r in route:
            print(r, end=" ")
        print()
