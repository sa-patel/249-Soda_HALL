from navigation import Navigation
from customObjects import RobotStatus, Order
from math import pi
test_waypoints = [
    (5, 0),
    (0, 10),
    (2, 10),
    (8, 10),
    (10, 10),
    (0, 5),
    (2, 5),
    (8, 5),
    (10, 5),
    (4, 10),
    (6, 10),
    (4, 5),
    (6, 5),
]
kobuki_state = [[RobotStatus.IDLE, [0,0,0], 0], [RobotStatus.IDLE, [0,0,0], 0]]
nav = Navigation(2, kobuki_state, waypoint_locations=test_waypoints)

def loop(data1):
    segment1 = nav.get_desired_segment(1, data1)
    if segment1 is not None:
        positional_error1, heading_error1, remaining_dist1 = nav.get_error_terms(data1["x"], data1["y"], data1["heading"], segment1)
        print("{}\t{:.2f}\t{:.2f}\t{:.2f}\t{}\t{:.2f}\t\t{:.2f}\t\t{:.2f}".format(
            kobuki_state[0][0], data1["x"], data1["y"], data1["heading"], 
            segment1, positional_error1, heading_error1, remaining_dist1
        ))
    else:
        print("{}\t{:.2f}\t{:.2f}\t{:.2f}\t{}\t\t\t-\t\t-\t\t-".format(
            kobuki_state[0][0], data1["x"], data1["y"], data1["heading"], 
            segment1
        ))

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
kobuki_state[0] = [RobotStatus.PLAN_PATH_TO_BASE, [], 0]
print("state\t\t\tx\ty\theading\tsegment\t\t\tpos error\thead error\tremaining dist")
for xyt in traj:
    data = {
        "x": xyt[0],
        "y": xyt[1],
        "heading": xyt[2],
    }
    loop(data)

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
print(kobuki_state[0])
kobuki_state[0] = [RobotStatus.PLAN_PATH_TO_TABLE, [Order("name", 2, 0, "water", 123), Order("name2", 1, 0, "juice", 456)], 2]
print(kobuki_state[0])
print("state\t\t\tx\ty\theading\tsegment\t\t\tpos error\thead error\tremaining dist")
for xyt in traj:
    data = {
        "x": xyt[0],
        "y": xyt[1],
        "heading": xyt[2],
    }
    loop(data)

# Deliver the second order
assert kobuki_state[0][0] == RobotStatus.LOADING_UNLOADING
print(kobuki_state[0])
kobuki_state[0][0] = RobotStatus.PLAN_PATH_TO_TABLE
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
