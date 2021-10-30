from random import randint

class BluetoothController:
    
    def __init__(self, device_id):
        self.device_id = device_id
        self.SRV_ID = "32e61089-2b22-4db5-a914-43ce41986c70"
        self.CHAR_DRIVE_ID = "32e6108c-2b22-4db5-a914-43ce41986c70"
        self.CHAR_DISP_ID = "32e6108d-2b22-4db5-a914-43ce41986c70"
        self.CHAR_BUTTON_ID = "32e6108e-2b22-4db5-a914-43ce41986c70"
        self.CHAR_TUNE_ID = "32e6108f-2b22-4db5-a914-43ce41986c70"
        self.kobuki_channel = 0
        if self.device_id == 1:
            self.UUID_ADDR = "C0:98:e5:49:00:FE" #kobuki#1
        else: 
            self.UUID_ADDR = "C0:98:e5:49:00:FF" #kobuki#2

    def connect(self):
        from bluepy.btle import Peripheral
        print("Attempting connection")
        while True:
            try:
                self.kobuki_controller = Peripheral(self.UUID_ADDR)
                print("Connected succesfully")
                sv = self.kobuki_controller.getServiceByUUID(self.SRV_ID)
                self.kobuki_channel = sv.getCharacteristics(self.CHAR_DRIVE_ID)[0]
                self.kobuki_display = sv.getCharacteristics(self.CHAR_DISP_ID)[0]
                self.kobuki_button = sv.getCharacteristics(self.CHAR_BUTTON_ID)[0]
                # self.kobuki_tune = sv.getCharacteristics(self.CHAR_TUNE_ID)[0]
                break
            except Exception as e:
                print(e)
                print("failed to connect. retrying...")


    def disconnect(self):
        if self.kobuki_channel is not None:
            self.kobuki_controller.disconnect()

    def connect_sim(self):
        # Use this for testing without bluetooth
        self.kobuki_channel = None
        self.kobuki_display = None
        self.kobuki_button = None

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
        MAX_INT = 32767
        MIN_INT = -32768
        byte_send = lambda n: bytearray(int(max(min(n, MAX_INT), MIN_INT)).to_bytes(2, 'big', signed=True))
        send_kobuki_bytes_0 = byte_send(positional_error_scaled_100x)
        send_kobuki_bytes_1 = byte_send(heading_error_scaled_100x)
        send_kobuki_bytes_2 = byte_send(remaining_dist_scaled_100x)
        send_kobuki_bytes_0.append(send_kobuki_bytes_1[0])
        send_kobuki_bytes_0.append(send_kobuki_bytes_1[1])
        send_kobuki_bytes_0.append(send_kobuki_bytes_2[0])
        send_kobuki_bytes_0.append(send_kobuki_bytes_2[1])
        if self.kobuki_channel is not None:
            print(send_kobuki_bytes_0)
            while True:
                try:
                    self.kobuki_channel.write(send_kobuki_bytes_0)
                    break
                except Exception as e:
                    print(e)
                    print("transmit failed")
                    self.disconnect()
                    self.connect()
                    pass
                
        else:
            # print("sim bt", send_kobuki_bytes_0)
            pass

    def transmit_stop(self):
        """Stop the motors."""
        # TODO

    def receive_button_press(self):
        # Receive bluetooth data from kobuki
        if self.kobuki_button is not None:
            try:
                self.kobuki_button.write(bytes(0))
                button_state = bool(int(self.kobuki_button.read().hex()))
                #self.kobuki_button.write(bytes(0))
                return button_state
            except Exception as e:
                print(e)
                print("could not receive button press")
                self.disconnect()
                self.connect()
                self.receive_button_press()
        # Simulation:
        # return input("Button press {}? ".format(self.device_id))
        return randint(1,10) == 1

    def display_drink(self,drink):
        if self.kobuki_display is not None:
            self.kobuki_display.write(bytes(drink, 'utf-8'))
        else:
            print("Kobuki {} display: {}".format(self.device_id, drink))

    def send_drinks_to_display(self, drinks):
        #self.display_drink("start")
        #for item in drinks: 
        #   self.display_drink(item)
        #self.display_drink("stop")
        drinks_string = ",".join(drinks)
        self.display_drink(drinks_string)
    
    def send_pid_constants(self, kp_pos, kd_pos, kp_head, kd_head):
        while True:
            try:
                byte_send = lambda n: bytearray(int(max(min(n, MAX_INT), MIN_INT)).to_bytes(1, 'big', signed=True))
                send_kobuki_bytes = byte_send(kp_pos)
                send_kobuki_bytes.append(byte_send(kd_pos[0]))
                send_kobuki_bytes.append(byte_send(kp_head[0]))
                send_kobuki_bytes.append(byte_send(kd_head[0]))
                break
            except:
                "pid send failed"
                continue
