import struct 
from bluepy.btle import Peripheral, DefaultDelegate 
import argparse

class BluetoothController:
    
    def __init__(self, device_id):
        self.device_id = device_id
        self.SRV_ID = "32e61089-2b22-4db5-a914-43ce41986c70"
        self.CHAR_DRIVE_ID = "32e6108c-2b22-4db5-a914-43ce41986c70"
        self.CHAR_DISP_ID = "32e6108d-2b22-4db5-a914-43ce41986c70"
        self.CHAR_BUTTON_ID = "32e6108e-2b22-4db5-a914-43ce41986c70"
        self.kobuki_channel = 0
        if self.device_id == 1:
            self.UUID_ADDR = "C0:98:e5:49:00:01" #kobuki#1
        else: 
            self.UUID_ADDR = "C0:98:e5:49:00:02" #kobuki#2

    def connect(self): 
        print("Attempting connection")
        kobuki_controller = Peripheral(self.UUID_ADDR)
        print("Connected succesfully")
        sv = kobuki_controller.getServiceByUUID(self.SRV_ID)
        self.kobuki_channel = sv.getCharacteristics(self.CHAR_DRIVE_ID)[0]
        self.kobuki_display = sv.getCharacteristics(self.CHAR_DISP_ID)[0]
        self.kobuki_button = sv.getCharacteristics(self.CHAR_BUTTON_ID)[0]

    def connect_sim(self):
        # Use this for testing without bluetooth
        self.kobuki_channel = None

    def transmit(self):
        led_state = bool(int(self.kobuki_channel.read().hex()))
        self.kobuki_channel.write(bytes([not led_state]))

    def transmit_nav(self, positional_error, heading_error, remaining_dist):
        SCALE_FACTOR = 100
        #positional_err = bytes(hex(int(positional_error)))
        #self.kobuki_channel.write(bytes([1,1]))
        #self.kobuki_channel.write(bytearray([1,2]))
        #self.kobuki_channel.write(bytes(positional_error))
        #self.kobuki_channel.write(bytes([not led_state]))
        positional_error_scaled_100x = positional_error * SCALE_FACTOR #312
        heading_error_scaled_100x = heading_error * SCALE_FACTOR #1323
        remaining_dist_scaled_100x = remaining_dist * SCALE_FACTOR
        send_kobuki_bytes_0 = bytearray(int(positional_error_scaled_100x).to_bytes(2,'big'))
        send_kobuki_bytes_1 = bytearray(int(heading_error_scaled_100x).to_bytes(2,'big'))
        send_kobuki_bytes_2 = bytearray(int(remaining_dist_scaled_100x).to_bytes(2, 'big'))
        send_kobuki_bytes_0.append(send_kobuki_bytes_1[0])
        send_kobuki_bytes_0.append(send_kobuki_bytes_1[1])
        send_kobuki_bytes_0.append(send_kobuki_bytes_2[0])
        send_kobuki_bytes_0.append(send_kobuki_bytes_2[1])
        if self.kobuki_channel is not None:
            print(send_kobuki_bytes_0)
            self.kobuki_channel.write(send_kobuki_bytes_0)
        else:
            # print("sim bt", send_kobuki_bytes_0)
            pass

    def transmit_stop(self):
        """Stop the motors."""
        # TODO

    def receive_button_press(self):
        # TODO receive bluetooth data from kobuki
        self.kobuki_press.write(bytes(0))
        button_state = bool(int(self.kobuki_press.read().hex()))
        return button_state

    def display_drink(self,drink): 
        self.kobuki_display.write(bytes(drink, 'utf-8'))
