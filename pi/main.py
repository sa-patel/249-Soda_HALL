"""main.py
Main module which calls other modules to implement the robot waiter.

Running:
python3 main.py
"""

# External libraries
import time
import threading

# Project modules
from navigation import NavGraph, WAYPOINTS, WAYPOINT_EDGES
from bluetooth import BluetoothController
from webcam import Webcam
from orderScheduler import OrderScheduler
from customObjects import RobotStatus
import server

LOOP_PERIOD = 0.25 # Period, in seconds, of the main loop.
NUM_KOBUKIS = 2

def main_loop():
    bt1 = BluetoothController(1)
    bt2 = BluetoothController(2)

    # Connect to nrf bluetooth
    # bt1.connect()
    # bt2.connect()

    # Simulate bluetooth connection when testing without nrf
    bt1.connect_sim()
    bt2.connect_sim()

    webcam = Webcam()

    coords = webcam.get_static_data()
    waypoints = [Waypoint(i, coords[i]) for i in range(13)]

    nav_graph = NavGraph()
    for w_i in WAYPOINTS:
        nav_graph.add_node(waypoints[w_i])
    for w_i, w_j in WAYPOINT_EDGES:
        nav_graph.connect_nodes(waypoints[w_i], waypoints[w_j])

    waiter1 = KobukiRobot(1, nav_graph)
    waiter2 = KobukiRobot(2, nav_graph)
    waiter1.set_home = waypoints[BASE_STATION_ID]
    waiter2.set_home = waypoints[BASE_STATION_ID]

    while True:
        data = webcam.get_data()
        data1 = data["kobuki1"]
        data2 = data["kobuki2"]

        bt_data1 = bt1.receive()
        bt_data2 = bt2.receive()

        # TODO: Push the button on the Kobuki if the bt tells us to

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
