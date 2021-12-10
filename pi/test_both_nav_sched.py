from navigation import Navigation
from bluetooth import BluetoothController
from orderScheduler import OrderScheduler
from customObjects import RobotStatus
from math import pi, sin, cos
from random import gauss
from time import sleep
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

kobuki_state = [[RobotStatus.IDLE, [], 0], [RobotStatus.IDLE, [], 0]]
bt1 = BluetoothController(1)
bt2 = BluetoothController(2)

# Simulate bluetooth connection when testing without nrf
bt1.connect_sim()
bt2.connect_sim()

scheduler = OrderScheduler(2, kobuki_state, bt1, bt2)

NUM_KOBUKIS = 2
nav = Navigation(NUM_KOBUKIS, kobuki_state, waypoint_locations=test_waypoints)

def noise(sigma):
    return gauss(0, sigma)

data = {
    "kobuki1": {
        "x": 4.9,
        "y": 0,
        "heading": 0,
    },
    "kobuki2": {
        "x": 5.1,
        "y": 0,
        "heading": 1,
    },
}

format_string = "{:28}{:6.2f}{:6.2f}{:9.2f}{:>20} {:28}{:6.2f}{:6.2f}{:9.2f}{:>20}"
header_format_string = "{:28}{:6}{:6}{:9}{:>20} {:28}{:6}{:6}{:9}{:>20}"

# Boundaries for testing
xL, xU = -2, 12
yL, yU = -2, 12

def loop():
    data1 = data["kobuki1"]
    data2 = data["kobuki2"]
    scheduler.allocate()
    segment1 = nav.get_desired_segment(1, data1)
    segment2 = nav.get_desired_segment(2, data2)
    bots = ((data1, segment1, bt1, kobuki_state[0]),
            (data2, segment2, bt2, kobuki_state[1]))
    for bot_data, segment, bt, state in bots:
        if segment is None:
            bt.transmit_nav(0, 0, 0)
        else:
            positional_error, heading_error, remaining_dist = nav.get_error_terms(bot_data["x"], bot_data["y"], bot_data["heading"], segment)
            bt.transmit_nav(positional_error, heading_error, remaining_dist)
            
            # Drive the bot (for simulation only)
            theta = segment.segment_angle()
            DECAY = 0.5
            STEP = 0.5 # meters
            d = min(STEP, remaining_dist)
            # heading = noisy_theta - heading_error
            heading = bot_data["heading"] - heading_error + noise(0.2)
            if heading < -pi:
                heading += 2*pi
            elif heading > pi:
                heading -= 2*pi
            bot_data["heading"] = heading
            bot_data["x"] += d*sin(heading) - DECAY*positional_error*cos(-theta)
            bot_data["y"] += d*cos(heading) - DECAY*positional_error*sin(-theta)
            assert(bot_data["x"] > xL and bot_data["x"] < xU)
            assert(bot_data["y"] > yL and bot_data["y"] < yU)
    
    print(format_string.format(
            kobuki_state[0][0], data1["x"], data1["y"], data1["heading"], 
            segment1.__str__(),
            kobuki_state[1][0], data2["x"], data2["y"], data2["heading"], 
            segment2.__str__(),
        ))



scheduler.create("Amit",1,"Gin",0)
scheduler.create("Zak",2,"Rum",0)
scheduler.create("Sagar",3,"Beer",0)
scheduler.create("Max",4,"Vodka",0)
scheduler.create("Amit",1,"Whiskey",0)
scheduler.create("Zak",2,"Tequila",0)
scheduler.create("Sagar",3,"Seltzer",0)
scheduler.create("Max",4,"Pop",0)

print_header = header_format_string.format("Status", "x", "y", "heading", "segment", "Status", "x", "y", "heading", "segment")
print(print_header)
prev_idles = 0
while scheduler.queue.size > 0 or prev_idles < 5:
    loop()
    # Keep track of idle states and end the simulation when both robots stay idle.
    if kobuki_state[0][0] == RobotStatus.IDLE and kobuki_state[1][0] == RobotStatus.IDLE:
        prev_idles += 1
    else:
        prev_idles = 0
    # sleep(0.1)