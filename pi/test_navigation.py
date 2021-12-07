from navigation import Navigation
from customObjects import RobotStatus
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
    (5, 10),
    (5, 5),
]
kobuki_state = [(RobotStatus.IDLE, [0,0,0], 0), (RobotStatus.IDLE, [0,0,0], 0)]
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

traj = [
    (10, 10.1, -pi/2),
    (10, 10.1, -pi/2),
    (9, 9.9, -pi/2),
    (8, 10.00, -pi/2),
    (7, 10, -pi/2),
    (5.4, 11, -pi/2),
    (5, 10, pi),
    (4.9, 9, pi),
    (4.9, 8, 3.0),
    (5, 7, pi),
    (5, 5, pi),
    (5, 3, pi),
    (5, 0.1, pi),
    (5, 0, pi),
    (5, 0, pi),
    (5, 0, pi),
]

# Test bench
kobuki_state[0] = (RobotStatus.PLAN_PATH_TO_BASE, [], 0)
print("state\t\t\tx\ty\theading\tsegment\t\t\tpos error\thead error\tremaining dist")
for xyt in traj:
    data = {
        "x": xyt[0],
        "y": xyt[1],
        "heading": xyt[2],
    }
    loop(data)
