import time
from bluetooth import BluetoothController

bt1 = BluetoothController(1)
bt2 = BluetoothController(2)
bt1.connect()
bt2.connect()

time.sleep(2)

sample_data_1 = [0, 0, 10.0]
sample_data_2 = [10, 10, 10.0]

for i in range(1000):
    bt1.transmit_nav(*sample_data_1)
    bt2.transmit_nav(*sample_data_2)
    sample_data_1[2] -= 0.01
    sample_data_2[2] -= -0.01
    time.sleep(0.25)
bt1.transmit_nav(0,0,0)
