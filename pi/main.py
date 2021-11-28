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
import server

bt1 = BluetoothController(1)
bt2 = BluetoothController(2)
webcam = Webcam()
scheduler = OrderScheduler()
NUM_KOBUKIS = 2
nav = Navigation(NUM_KOBUKIS, scheduler)
LOOP = 0.25 # Period, in seconds, of the main loop.

def loop():
    data = webcam.get_data()
    data1 = data["kobuki1"]
    data2 = data["kobuki2"]
    segment1 = nav.get_desired_segment(1)
    positional_error1, heading_error1 = nav.get_error_terms(data1["x"], data1["y"], data1["heading"], segment1)
    bt1.transmit(positional_error1, heading_error1)

def loop_entry():
    while True:
        loop()
        time.sleep(LOOP)

if __name__ == "__main__":
    loop_thread = threading.Thread(target=loop_entry)
    loop_thread.start()
    server.start(scheduler)
