from navigation import *
from customObjects import RobotStatus, Order
from bluetooth import BluetoothController
from waiter import KobukiRobot
from math import pi
waypoint_locations = [
    (5, 0),
    (0, 10),
    (2, 10),
    (4, 10),
    (6, 10),
    (8, 10),
    (10, 10),
    (0, 5),
    (2, 5),
    (4, 5),
    (6, 5),
    (8, 5),
    (10, 5),
]

waypoints = [Waypoint(i, waypoint_locations[i]) for i in range(NUM_WAYPOINTS)]
nav_graph = NavGraph()

for w_i in waypoints:
    # nav_graph.add_node(waypoints[w_i])
    nav_graph.add_node(w_i)
for w_i, w_j in WAYPOINT_EDGES:
    # nav_graph.connect_nodes(waypoints[w_i], waypoints[w_j])
    nav_graph.connect_nodes(waypoints[w_i], waypoints[w_j])
waiter1 = KobukiRobot(1, nav_graph)
# waiter2 = KobukiRobot(2, nav_graph)
waiter1.set_home(waypoints[BASE_STATION_ID])
# waiter2.set_home(waypoints[BASE_STATION_ID])

bt1 = BluetoothController(1)
# bt2 = BluetoothController(2)

bt1.connect_sim()
# bt2.connect_sim()

def loop(data1, button1):

    if button1:
        waiter1.push_button()
    # if button2:
    #     waiter2.push_button()

    waiter1.update(data1)
    # waiter2.update(data2)
    bt1.transmit_nav(*waiter1.get_heading(data1))
    # bt2.transmit_nav(*waiter1.get_heading())
    
    if waiter1.get_status() == RobotStatus.MOVING:
        x0, y0 = waiter1.prev_waypoint.coords
        x1, y1 = waiter1.next_waypoint.coords
        segment1 = Segment(x0, y0, x1, y1)

        positional_error1, heading_error1, remaining_dist1 = waiter1.get_heading()
        print("{:.2f}\t{:.2f}\t{:.2f}\t{}\t{:.2f}\t\t{:.2f}\t\t{:.2f}".format(
            data1["x"], data1["y"], data1["heading"], 
            segment1, positional_error1, heading_error1, remaining_dist1
        ))
    else:
        pass

# Test returning to base station
traj = [
    (10, 10.1, -pi/2),
    (10, 10.1, -pi/2),
    (9, 9.9, -pi/2),
    (8, 10.00, -pi/2),
    (7, 10, -pi/2),
    (6.4, 11, -pi/2),
    (6, 10, pi),
    (5.9, 9, pi),
    (5.9, 8, 3.0),
    (6, 7, pi),
    (6, 5, pi),
    (6, 3, pi),
    (5.5, 1.1, pi),
    (5, 0.1, pi),
    (5, 0, pi),
    (5, 0, pi),
]

print("test returning to base station")
print("state\t\t\tx\ty\theading\tsegment\t\t\tpos error\thead error\tremaining dist")
for xyt in traj:
    data = {
        "x": xyt[0],
        "y": xyt[1],
        "heading": xyt[2],
    }
    button = True
    loop(data, button)

# Test delivering order
traj = [
    (5, 0, 0),
    (5, 0, 0),
    (4.9, 2, 0),
    (4, 5, 0.1),
    (4, 5, -pi/2),
    (3, 5, -pi/2),
    (3, 4.5, -1.5),
    (2, 5.1, -pi/2),
    (-0.1, 5, -pi/2),
    (0, 5, -pi/2),
]
print("test delivering order")
# print(kobuki_state[0])
# kobuki_state[0] = [RobotStatus.PLAN_PATH_TO_TABLE, [Order("name", 2, 0, "water", 123), Order("name2", 1, 0, "juice", 456)], 2]
# print(kobuki_state[0])
print("state\t\t\tx\ty\theading\tsegment\t\t\tpos error\thead error\tremaining dist")
for xyt in traj:
    data = {
        "x": xyt[0],
        "y": xyt[1],
        "heading": xyt[2],
    }
    loop(data)

# Deliver the second order
# assert kobuki_state[0][0] == RobotStatus.UNLOADING
# print(kobuki_state[0])
# kobuki_state[0][0] = RobotStatus.PLAN_PATH_TO_TABLE
traj = [
    (0, 5, -pi/2),
    (0, 5, pi/2),
    (2, 5, pi/2),
    (3, 5, pi/2),
    (4, 5, pi/4),
    (4, 5, 0),
    (4, 10, 0),
    (4, 10, 0),
    (4, 10, -pi/2),
    (3, 10, -pi/2),
    (2, 10, -pi/2),
    (2, 10, -pi/2),
]
for xyt in traj:
    data = {
        "x": xyt[0],
        "y": xyt[1],
        "heading": xyt[2],
    }
    loop(data)
