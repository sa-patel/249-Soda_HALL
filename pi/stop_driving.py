import time
from bluetooth import BluetoothController

bt1 = BluetoothController(1)
bt2 = BluetoothController(2)
bt1.connect()
bt2.connect()

time.sleep(2)

sample_data_1 = [0, 0, 10.0]
sample_data_2 = [10, 10, 10.0]

bt1.transmit_nav(0,0,0)
bt2.transmit_nav(0,0,0)
