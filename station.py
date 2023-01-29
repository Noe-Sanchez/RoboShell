#!/usr/bin/env python
import sys
from digi.xbee.devices import XBeeDevice, XBee64BitAddress, RemoteXBeeDevice, XBeeNetwork

if len(sys.argv) < 2:
    "Not enough arguments\n\nUsage:\n\npython3 roboshell_client.py XBEE_PORT\n"
xbee_port = sys.argv[1]
remote_id = "BOAT_XBEE"

device = XBeeDevice(xbee_port, 9600)
print("> Bound to station xbee")

onHold = False

def data_callback(xbee_message):
    print(xbee_message.data.decode())
    global onHold
    onHold = False

def main():
    global onHold
    try:
        device.open()

        print("> Trying to find", remote_id, end="")
        xbee_network = device.get_network()
        remote_device = xbee_network.discover_device(remote_id)

        if remote_device is None:
            print(" ...could not find", remote_id)
            exit(1)

        print(" ...found", remote_id)
        device.add_data_received_callback(data_callback)

        print("> RoboShell online")

        while True:
            if not onHold:
                outgoing_data = input("> RoboShell:$ ")
                
                #Custom command catching
                if outgoing_data.strip().lower() == "exit":
                    print('> Closing xbee connection')
                    device.close()
                    print("> Closing RoboShell")
                    exit(1)
                else:
                    onHold = True
                    device.send_data(remote_device, outgoing_data)

    finally:
        if device is not None and device.is_open():
            device.close()
            print('\n> Closed xbee connection')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("> Closing RoboShell")
