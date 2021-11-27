"""main.py
Main module which calls other modules to implement the robot waiter.

Running:
python3 main.py
"""
from navigation import Navigation
from bluetooth import BluetoothController
from webcam import Webcam
import server
import time
from multiprocessing import Process

bt1 = BluetoothController(1)
bt2 = BluetoothController(2)
webcam = Webcam()
nav = Navigation(2)
LOOP = 0.25 # Period, in seconds, of the main loop.

def loop():
    data = webcam.get_data()
    data1 = data["kobuki1"]
    data2 = data["kobuki2"]
    segment1 = nav.get_desired_segment(1)
    positional_error1, heading_error1 = nav.get_error_terms(data1["x"], data1["y"], data1["heading"], segment1)
    bt1.transmit(positional_error1, heading_error1)
    print(time.time())

def loop_entry():
    while True:
        loop()
        time.sleep(LOOP)

if __name__ == "__main__":
    loop_proc = Process(target=loop_entry)
    loop_proc.start()
    server.start()
    loop_proc.join()
