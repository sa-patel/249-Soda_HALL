"""main.py
Main module which calls other modules to implement the robot waiter.

Running:
python3 main.py
"""
from navigation import Navigation
from bluetooth import BluetoothController
from webcam import Webcam

bt1 = Bluetooth(1)
bt2 = Bluetooth(2)
webcam = Webcam()
nav = Navigation()

def loop():
    data = webcam.get_data()
    data1 = data["kobuki1"]
    data2 = data["kobuki2"]
    segment1 = nav.get_desired_segment(1)
    error1 = nav.get_error_terms(data1["x"], data1["y"], data1["heading"])
    bt1.transmit(error1)

if __name__ == "__main__":
    while True:
        loop()
