"""main.py
Main module which calls other modules to implement the robot waiter.

Running:
python3 main.py
"""

# External libraries
import time
import threading
from orderScheduler import OrderScheduler

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

webcam = Webcam()
coords = webcam.get_static_data()
waypoints = [Waypoint(i, (100.0, 100.0)) for i in range(NUM_WAYPOINTS)]
nav_graph = NavGraph()

for w_i in waypoints:
    nav_graph.add_node(waypoints[w_i])
for w_i, w_j in WAYPOINT_EDGES:
    nav_graph.connect_nodes(waypoints[w_i], waypoints[w_j])

waiter1 = KobukiRobot(1, nav_graph)
waiter2 = KobukiRobot(2, nav_graph)
waiter1.set_home(waypoints[BASE_STATION_ID])
waiter2.set_home(waypoints[BASE_STATION_ID])

scheduler = OrderScheduler([waiter1, waiter2], waypoints)

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
        data = webcam.get_data()
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

        time.sleep(LOOP_PERIOD)

if __name__ == "__main__":
    loop_thread = threading.Thread(target=main_loop)
    loop_thread.start()
    server.start(scheduler)
