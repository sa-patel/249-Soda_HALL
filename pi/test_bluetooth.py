import time
from bluetooth import BluetoothController
SCALE_FACTOR = 100

kobuki_1 = BluetoothController(1)
#kobuki_2 = BluetoothController(2)
kobuki_1.connect()

time.sleep(4)
positional_error = 3.65 #meters 
heading_error = 13.23 #degrees
remaining_dist = 1000
positional_error_scaled_100x = positional_error * SCALE_FACTOR #312
heading_error_scaled_100x = heading_error * SCALE_FACTOR #1323
print((int(positional_error_scaled_100x).to_bytes(2,'big')))
print(int(heading_error_scaled_100x).to_bytes(2,'big'))
print(((int(positional_error_scaled_100x).to_bytes(2,'big').hex())))
print((int(heading_error_scaled_100x).to_bytes(2,'big').hex()))
kobuki_1.transmit_nav(positional_error,heading_error,remaining_dist)
time.sleep(10)
