from navigation import *
from bluetooth import BluetoothController
from orderScheduler import OrderScheduler
from customObjects import RobotStatus
from waiter import KobukiRobot
from math import pi, sin, cos
from random import gauss
from time import sleep
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
waypoint_locations = [
    (4, 0),
    (6, 0),
    (0, 10),
    (4, 10),
    (6, 10),
    (10, 10),
    (0, 5),
    (4, 5),
    (6, 5),
    (10, 5),
    ]

waypoints = [Waypoint(i, waypoint_locations[i]) for i in range(NUM_WAYPOINTS)]
nav_graph = NavGraph()

for w_i in waypoints:
    nav_graph.add_node(w_i)
for w_i, w_j in WAYPOINT_EDGES:
    nav_graph.connect_nodes(waypoints[w_i], waypoints[w_j])

NUM_KOBUKIS = 2
waiter1 = KobukiRobot(1, nav_graph)
waiter2 = KobukiRobot(2, nav_graph)
waiter1.set_home(waypoints[BASE_STATION_1])
waiter2.set_home(waypoints[BASE_STATION_2])
bt1 = BluetoothController(1)
bt2 = BluetoothController(2)

# Simulate bluetooth connection when testing without nrf
bt1.connect_sim()
bt2.connect_sim()

scheduler = OrderScheduler([waiter1, waiter2], waypoints)

def noise(sigma):
    return gauss(0, sigma)

data = {
    "kobuki1": [4.0, 0, 0],
    "kobuki2": [6, 0, 0],
}

format_string = "{:28}{:6.2f}{:6.2f}{:9.2f} w_next={:<3} {:28}{:6.2f}{:6.2f}{:9.2f} w_next={:<3}"
header_format_string = "{:28}{:6}{:6}{:9}{:>20} {:28}{:6}{:6}{:9}{:>20}"

# Boundaries for testing
xL, xU = -2, 12
yL, yU = -2, 12

x1 = []
y1 = []
x2 = []
y2 = []

def loop():
    data1 = data["kobuki1"]
    data2 = data["kobuki2"]
    button1 = bt1.receive_button_press()
    button2 = bt2.receive_button_press()
    if button1:
        waiter1.push_button()
    if button2:
        waiter2.push_button()

    scheduler.allocate()
    waiter1.update(data1)
    waiter2.update(data2)

    bots = ((data1, waiter1, bt1),
            (data2, waiter2, bt2))
    
    for bot_data, waiter, bt in bots:
        positional_error, heading_error, remaining_dist = waiter.get_heading(bot_data)
        #if waiter.no == 1:
            #print(waiter.no, "'s error:", waiter.get_heading(bot_data))
        bt.transmit_nav(positional_error, heading_error, remaining_dist)
        if abs(positional_error) > 0 or abs(heading_error) > 0 or abs(remaining_dist) > 0:
            # Drive the bot (for simulation only)
            theta = waiter.segment.segment_angle()
            DECAY = 0.5
            STEP = 0.5 # meters
            d = min(STEP, remaining_dist)
            # heading = noisy_theta - heading_error
            heading = bot_data[2] - heading_error + noise(0.2)
            if heading < -pi:
                heading += 2*pi
            elif heading > pi:
                heading -= 2*pi
            bot_data[2] = heading
            bot_data[0] += d*sin(heading) - DECAY*positional_error*cos(-theta)
            bot_data[1] += d*cos(heading) - DECAY*positional_error*sin(-theta)
            #if waiter.no == 1:
                #print(bot_data)
            assert(bot_data[0] > xL and bot_data[0] < xU)
            assert(bot_data[1] > yL and bot_data[1] < yU)
        else:
            bt.transmit_nav(positional_error, heading_error, remaining_dist)
    
    print(format_string.format(
            waiter1.get_status(), data1[0], data1[1], data1[2], 
            waiter1.prev_waypoint.ident,
            waiter2.get_status(), data2[0], data2[1], data2[2], 
            waiter2.prev_waypoint.ident,
        ))
    x1.append(data1[0])
    x2.append(data2[0])
    y1.append(data1[1])
    y2.append(data2[1])

    # sleep(0.1)



# scheduler.create("Amit",1,"Gin",0)
# scheduler.create("Zak",2,"Rum",0)
# scheduler.create("Sagar",3,"Beer",0)
# scheduler.create("Max",6,"Vodka",0)
# scheduler.create("Amit2",5,"Cola",0)
# scheduler.create("Amit",1,"Whiskey",0)
# scheduler.create("Zak",2,"Tequila",0)
# scheduler.create("Sagar",3,"Seltzer",0)
# scheduler.create("Max",6,"Pop",0)

scheduler.create("Amit",1,"Gin",0)
scheduler.create("Zak",2,"Rum",0)
scheduler.create("Sagar",3,"Beer",0)
scheduler.create("Max",4,"Vodka",0)
scheduler.create("Amit2",1,"Cola",0)
scheduler.create("Amit",2,"Whiskey",0)
scheduler.create("Zak",3,"Tequila",0)
scheduler.create("Sagar",3,"Seltzer",0)
scheduler.create("Max",6,"Pop",0)

print_header = header_format_string.format("Status", "x", "y", "heading", "segment", "Status", "x", "y", "heading", "segment")
print(print_header)
while scheduler.queue.size > 0 or len(waiter1.destinations) > 0 or len(waiter2.destinations) > 0 or waiter1.get_status() is not RobotStatus.LOADING or waiter2.get_status() is not RobotStatus.LOADING:
    # try:
        loop()
        # sleep(0.1)
    # except Exception as e:
    #     print(e)
    #     break
print("done")
fig = plt.figure(figsize=(14, 9))
ax = fig.add_subplot(xlim = (-1, 11), ylim = (-1, 11))
history1=[[],[]]
history2=[[],[]]
travel_line = [ax.plot([], [], 'bg'[i])[0] for i in range(NUM_KOBUKIS)]
bots = [ax.plot([], [], 'bg'[i]+'o', markersize=16)[0] for i in range(NUM_KOBUKIS)]

def update(i):
    history1[0].append(x1[i])
    history1[1].append(y1[i])
    history2[0].append(x2[i])
    history2[1].append(y2[i])
    bots[0].set_data([x1[i], y1[i]])
    bots[1].set_data([x2[i], y2[i]])
    travel_line[0].set_data(history1)
    travel_line[1].set_data(history2)

ani = animation.FuncAnimation(
    fig, update, len(x1), interval=90, repeat=False
)

table1_rect = np.array([[1, 3, 3, 1, 1],[6, 6, 9, 9, 6]])
table2_rect = table1_rect + np.array([6,0]).reshape(2,1)
delivery_i = (2,3,4,5,6,7,8,9)
intermediate_i = ()
delivery_locations = []
intermediate_locations = []
for i in delivery_i:
    delivery_locations.append(waypoint_locations[i])
for i in intermediate_i:
    intermediate_locations.append(waypoint_locations[i])
delivery_locations = np.array(delivery_locations).T
intermediate_locations = np.array(intermediate_locations).T
plt.plot(table1_rect[0], table1_rect[1], 'r')
plt.plot(table2_rect[0], table2_rect[1], 'r')
plt.plot(delivery_locations[0], delivery_locations[1], 'b+')
# plt.plot(intermediate_locations[0], intermediate_locations[1], 'mx')
plt.plot([4, 6],[0, 0],'ro')
plt.show()