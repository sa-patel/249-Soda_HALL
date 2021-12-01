import struct 
from bluepy.btle import Peripheral, DefaultDelegate 
import argparse

class BluetoothController:

    def __init__(self, device_id):
        self.device_id = device_id
        self.SRV_ID = "32e61089-2b22-4db5-a914-43ce41986c70"
        self.CHAR_DRIVE_ID = "32e6108C-2b22-4db5-a914-43ce41986c70"
        self.kobuki_channel = 0
        if self.device_id == 1:
            self.UUID_ADDR = "C0:98:E5:49:00:01" #kobuki#1
        else: 
            self.UUID_ADDR = "C0:98:E5:49:00:02" #kobuki#2

    def connect(self): 
        print("Attempting connection")
        kobuki_controller = Peripheral(self.UUID_ADDR)
        print("Connected succesfully")
        sv = kobuki_controller.getServiceByUUID(self.SRV_ID)
        self.kobuki_channel = sv.getCharacteristics(self.CHAR_DRIVE_ID)[0]


    def transmit(self):
        led_state = bool(int(self.kobuki_channel.read().hex()))
        self.kobuki_channel.write(bytes([not led_state]))

    def transmit_nav(self, positional_error, heading_error):
        led_state = bool(int(self.kobuki_channel.read().hex()))
        self.kobuki_channel.write(bytes([not led_state]))
        




