import time
from bluetooth import BluetoothController

kobuki_1 = BluetoothController(1)
#kobuki_2 = BluetoothController(2)
kobuki_1.connect()

time.sleep(5)

kobuki_1.transmit()