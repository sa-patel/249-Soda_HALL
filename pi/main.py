"""main.py
Main module which calls other modules to implement the robot waiter.

Running:
python3 main.py
"""

# External libraries
import time
import threading

# Project modules
from navigation import Navigation
from bluetooth import BluetoothController
from webcam import Webcam
from orderScheduler import OrderScheduler
from customObjects import RobotStatus
import server

kobuki_state = [[RobotStatus.IDLE, [], 0], [RobotStatus.IDLE, [], 0]] # 3-list [STATE, Orders, NUM_DRINKS] for each robot
bt1 = BluetoothController(1)
bt2 = BluetoothController(2)

# Connect to nrf bluetooth
# bt1.connect()
# bt2.connect()

# Simulate bluetooth connection when testing without nrf
bt1.connect_sim()
bt2.connect_sim()

webcam = Webcam()
scheduler = OrderScheduler(2, kobuki_state)
NUM_KOBUKIS = 2
nav = Navigation(NUM_KOBUKIS, kobuki_state)
LOOP = 0.25 # Period, in seconds, of the main loop.

def loop():
    data = webcam.get_data()
    data1 = data["kobuki1"]
    data2 = data["kobuki2"]
    bt_data1 = bt1.receive()
    bt_data2 = bt2.receive()
    scheduler.allocate()
    segment1 = nav.get_desired_segment(1, data1)
    if segment1 is None:
        # Stop driving
        bt1.transmit_nav(0, 0, 0)
    else:
        positional_error1, heading_error1, remaining_dist1 = nav.get_error_terms(data1["x"], data1["y"], data1["heading"], segment1)
        bt1.transmit_nav(positional_error1, heading_error1, remaining_dist1)

def loop_entry():
    while True:
        loop()
        time.sleep(LOOP)

if __name__ == "__main__":
    loop_thread = threading.Thread(target=loop_entry)
    loop_thread.start()
    server.start(scheduler)
