"""navigation.py
Plans the routes for each robot and keeps the robots on their track.
"""

"""waypoints:
     1       2      9       3       4
     _________              _________
    |         |            |         |
    |_________|            |_________|
     5        6     10      7        8

                    0
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
            visit, history = queue.pop()
            if visit == b:
                return history+[b]
            for i in self.adj[visit]:
                if i not in visited:
                    visited.append(i)
                    queue.append((i, history+[visit]))
        return None # No route found
class Navigation:
    # x y coordinates of base station
    base_station_x = None
    base_station_y = None
    all_edges = (
        (0, 10),
        (10, 6),
        (6, 5),
        (10, 7),
        (7, 8),
        (10, 9),
        (9, 2),
        (2, 1),
        (9, 3),
        (3, 4)
    )
    waypoint_locations = [
        # Index is waypoint id. Value is (x,y) tuple.
        # TODO fill this in once environment is defined.
    ]
    route = [] # List of upcoming waypoints.
    current_segment = None

    # Constants
    NUM_WAYPOINTS = 11
    DISTANCE_EPSILON = 0.15**2 # meters squared
    ALMOST_ZERO = 0.06**2
    def __init__(self, num_kobukis, kobuki_state, waypoint_locations = None):
        self.num_kobukis = num_kobukis
        self.kobuki_state = kobuki_state
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
        
       
        # Find error terms
        heading_error = heading - desired_segment.segment_angle()
        if heading_error > pi:
            heading_error -= 2*pi
        remaining_dist = norm_sq(x2-x, y2-y)**0.5
        segment_length = desired_segment.length_squared()**0.5
        if segment_length < self.ALMOST_ZERO:
            print("Error: segment length near zero")
        positional_error = ((x2-x1)*(y1-y)-(y2-y1)*(x1-x))/segment_length

        return positional_error, heading_error, remaining_dist
    
    def advance_current_segment(self):
        """Generate the next segment from self.route."""
        # Return False if route is completed.
        if len(self.route) < 2:
            return False

        point_a = self.route.pop(0)
        point_b = self.route[0]
        s = self.convert_waypoints_to_segment(point_a, point_b)
        # Ignore this segment if length is small
        if s.length_squared() < self.ALMOST_ZERO:
            return self.advance_current_segment()
        else:
            self.current_segment = s
        return True

    def point_reached(self, x, y, x2, y2):
        """Returns true if the points are within epsilon distance of each other"""
        dist_sq = norm_sq(x - x2, y - y2)
        return dist_sq < self.DISTANCE_EPSILON
    
    def get_desired_segment(self, kobuki_id, webcam_data):
        assert(0 < kobuki_id and kobuki_id <= self.num_kobukis)
        
        def advance_segment_check_state():
            # Get the next segment
            segments_remain = self.advance_current_segment()
            if not segments_remain:
                self.kobuki_state[kobuki_id-1] = RobotStatus.IDLE, order, num_drinks
                return None
            return self.current_segment

        state, order, num_drinks = self.kobuki_state[kobuki_id-1]
        if state == RobotStatus.IDLE:
            # stop the motors.
            return None
        elif state == RobotStatus.PLAN_PATH_TO_BASE:
            # Plan the route to the base station.
            self.route = [] # Clear any saved routes
            x0 = webcam_data["x"]
            y0 = webcam_data["y"]
            self.plan_path(x0, y0, 0) # Point 0 is base station.
            self.kobuki_state[kobuki_id-1] = RobotStatus.RETURNING, order, num_drinks
            return advance_segment_check_state()
        elif state == RobotStatus.RETURNING:
            # Drive the path to get the order from the base station.
            if self.current_segment is None:
                return advance_segment_check_state()
            else:
                #TODO go to the next segment once end of current segment is reached.
                # if x, y is close to xf, yf, move on to the next segment
                x0 = webcam_data["x"]
                y0 = webcam_data["y"]
                xf = self.current_segment.xf
                yf = self.current_segment.yf
                if self.point_reached(x0, y0, xf, yf):
                    return advance_segment_check_state()
                return self.current_segment
        elif state == RobotStatus.DELIVERING_ORDER:
            # Drive the path to get the order from base station to table.

            pass
        else:
            print("navigation state not implemented")
        return None

    def set_destination(self, kobuki_id, x, y):
        # TODO
        pass
    
    def set_base_station_location(self, x, y):
        self.base_station_x = x
        self.base_station_y = y

    def plan_path(self, x0, y0, destination):
        start = Waypoint("XY", (x0, y0))
        self.route.append(start)

        # Find the nearest defined waypoint.
        nearest = self.nearest_waypoint(x0, y0)

        # Make route to destination
        route = self.graph.bfs_route(nearest, destination)
        if route is not None:
            # Convert ints to Waypoints
            waypoint_route = [Waypoint("PREDEFINED", i) for i in route]
            self.route += waypoint_route
            # self.route_print()
        else:
            print("No route found")
            self.route = None
    
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
    
    def route_print(self):
        """Testing function to print the route"""
        print("route", end=" ")
        for r in self.route:
            print(r, end=" ")
        print()
