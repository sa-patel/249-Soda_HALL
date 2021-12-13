"""main.py
Main module which calls other modules to implement the robot waiter.

Running:
python3 main.py
"""

# External libraries
import sys
import time
import threading
from orderScheduler import OrderScheduler
from computerVision.CV_positioning_system import CV_positioning_system

# Project modules
from navigation import *
from bluetooth import BluetoothController
from webcam import Webcam
from orderScheduler import OrderScheduler
from customObjects import Waypoint
from waiter import KobukiRobot
import server

LOOP_PERIOD = 0.25 # Period, in seconds, of the main loop.
NUM_KOBUKIS = 2

pos_sys = CV_positioning_system()
ids_to_coords = pos_sys.get_stationary_positions()

waypoints = []
nav_graph = NavGraph()

for w_i in range(NUM_WAYPOINTS):
    if ids_to_coords.get(w_i) is None:
        print("ERROR: waypoint with id {} not present in image".format(w_i))
        wp = Waypoint(w_i, (100.0, 100.0))
        waypoints.append(wp)
        nav_graph.add_node(wp)
    else:
        print(w_i, ids_to_coords[w_i][:2])
        wp = Waypoint(w_i, ids_to_coords[w_i][:2])
        waypoints.append(wp)
        nav_graph.add_node(wp)


for w_i, w_j in WAYPOINT_EDGES:
    nav_graph.connect_nodes(waypoints[w_i], waypoints[w_j])

waiter1 = KobukiRobot(1, nav_graph)
waiter2 = KobukiRobot(2, nav_graph)
waiter1.set_home(waypoints[BASE_STATION_ID])
waiter2.set_home(waypoints[BASE_STATION_ID])

scheduler = OrderScheduler([waiter1, waiter2], waypoints)

def transmit_display(waiter, bt):
    """When loading drinks, transmit a list of drinks to display."""
    if waiter.get_status() == RobotStatus.LOADING:
        bt.send_drinks_to_display(waiter.drinks)
    # TODO transmit blank in other states?

def main_loop():
    bt1 = BluetoothController(1)
    bt2 = BluetoothController(2)

    # Connect to nrf bluetooth
    # bt1.connect()
    # bt2.connect()

    # Simulate bluetooth connection when testing without nrf
    bt1.connect_sim()
    bt2.connect_sim()
    #waypoints = [Waypoint(i, coords[i]) for i in range(13)]

    while True:
        data = pos_sys.get_robot_positions()
        return
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
        bt1.transmit_nav(*waiter1.get_heading())
        bt2.transmit_nav(*waiter1.get_heading())
        transmit_display(waiter1, bt1)
        transmit_display(waiter2, bt2)

        time.sleep(LOOP_PERIOD)

if __name__ == "__main__":
    loop_thread = threading.Thread(target=main_loop)
    loop_thread.start()
    server.start(scheduler)
