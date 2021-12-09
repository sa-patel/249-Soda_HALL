"""navigation.py
Plans the routes for each robot and keeps the robots on their track.
"""

"""
Waypoints:

C = Corner
X = Intermediate waypoint
B = Base station

  C           C---X---X---C           C
  | ╔═════════╗   |   |   ╔═════════╗ |
  | ║         ║   |   |   ║         ║ |
  | ╚═════════╝   |   |   ╚═════════╝ |
  C-----------C---X---X---C-----------C
                   \ /
                    B

Waypoint IDs:

  1           2---3---4---5           6
  | ╔═════════╗   |   |   ╔═════════╗ |
  | ║         ║   |   |   ║         ║ |
  | ╚═════════╝   |   |   ╚═════════╝ |
  7-----------8---9---10--11----------12
                   \ /
                    0

Seat numbers:
    ╔═════════╗           ╔═════════╗
    ║ 1     2 ║           ║5       6║
    ║ 3     4 ║           ║7       8║
    ╚═════════╝           ╚═════════╝
"""
# External libraries
import math

# Project modules
from customObjects import Segment, RobotStatus, Waypoint

class NavGraph:
    def __init__(self):
        # The graph is represented by an adjacency list,
        # which in Python is a dictionary mapping waypoints
        # to a list of other waypoints it's connected to
        self.adj_list = dict()
        self.locking_groups = []

    def add_node(self, w):
        # We use a list here to ensure consistent iteration order
        self.adj_list[w] = []

    def connect_nodes(self, waypoints):
        for w1, w2 in waypoints:
            if not self.adj_list.get(w1) or not self.adj_list.get(w2):
                raise Exception("Waypoints not found in graph!")

            self.adj_list[w1].append(w2)
            self.adj_list[w2].append(w1)

    def find_route(self, start, endpoints):
        """
        Calculates the shortest path from START to any
        of the waypoints in ENDPOINTS and returns
        the next hop in that path.
        """
        if start in endpoints:
            raise ValueError("START cannot also be in ENDPOINTS")

        visited = {}
        paths = [[start]]
        new_paths = []
        found = False

        while paths:
            path = paths.pop(0)
            end_node = path[-1]

            for neighbor in self.adj_list[end_node]:
                if neighbor not in visited:
                    new_path = path + [neighbor]

                    if neighbor in endpoints:
                        print("Path found:", new_path) # Debug
                        # Return the second node, which is the
                        # node connected to the starting point
                        return new_path

                    new_paths.append(new_path)

            visited.add(end_node)
            paths = new_paths
            new_paths = []

        # If we could not find a valid path, we should just stall
        return None

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
    table_to_waypoint = [ # Index is table number. Value is waypoint id.
        1, 2, 5, 6, 3, 4, 7, 8
    ]

    # Constants
    NUM_WAYPOINTS = 13
    DISTANCE_EPSILON = 0.15 # meters
    ALMOST_ZERO = 0.06**2
    def __init__(self, num_kobukis, kobuki_state, waypoint_locations = None):
        assert(len(kobuki_state) >= num_kobukis)
        self.num_kobukis = num_kobukis
        self.kobuki_state = kobuki_state
        self.route = [[] for _ in range(self.num_kobukis)] # List of upcoming waypoints
        self.current_segment = [None for _ in range(self.num_kobukis)]

        # Build the navigation graph
        self.graph = NavGraph(self.NUM_WAYPOINTS)
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
        remaining_dist = math.dist([x, y], [x2, y2])
        segment_length = desired_segment.length_squared()**0.5
        if segment_length < self.ALMOST_ZERO:
            print("Error: segment length near zero")
        positional_error = ((x2-x1)*(y1-y)-(y2-y1)*(x1-x))/segment_length

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
        dist_sq = math.dist([x, y], [x2, y2])
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
        if state == RobotStatus.LOADING_UNLOADING:
            # TODO handle a button press and advance to the next state
            # stop the motors.
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
            dest = self.convert_table_to_waypoint(order.pop(0).table)
            self.plan_path(kobuki_id, x0, y0, dest) # Point 0 is base station.
            self.kobuki_state[kobuki_id-1] = [RobotStatus.DELIVERING_ORDER, order, num_drinks]
            return advance_segment_check_state(RobotStatus.LOADING_UNLOADING)
        elif state == RobotStatus.DELIVERING_ORDER:
            # Drive the path to get the order to the table.
            if current_segment is None:
                return advance_segment_check_state(RobotStatus.LOADING_UNLOADING)
            else:
                # Determine the current segment.
                x0 = webcam_data["x"]
                y0 = webcam_data["y"]
                xf = current_segment.xf
                yf = current_segment.yf
                if self.point_reached(x0, y0, xf, yf):
                    return advance_segment_check_state(RobotStatus.LOADING_UNLOADING)
                return current_segment
        else:
            print("navigation state not implemented")
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
    
    def convert_table_to_waypoint(self, table):
        """Convert table number to waypoint number"""
        return self.table_to_waypoint[table]
    
    def route_print(self, kobuki_id):
        """Testing function to print the route"""
        print("route", end=" ")
        route = self.route[kobuki_id-1]
        for r in route:
            print(r, end=" ")
        print()
