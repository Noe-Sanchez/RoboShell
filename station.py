#!/usr/bin/env python
import sys
import curses
from Buffer_class import Buffer
from digi.xbee.devices import XBeeDevice

def cprint(buffer, str):
    buffer.addstr(str)
    buffer.refresh()

if len(sys.argv) < 2:
    print("Not enough arguments\n\nUsage:\n\npython3 roboshell_client.py XBEE_PORT\n")
    exit(1)

xbee_port = sys.argv[1]
remote_id = "BOAT_XBEE"

w = curses.initscr()
lines = 42
columns = 150

half_width = int(columns / 2)

left_window = curses.newwin(lines, half_width)
lb = Buffer(left_window, lines)

right_window = curses.newwin(lines, half_width, 0, half_width + 2)
rb = Buffer(right_window, lines)

device = XBeeDevice(xbee_port, 9600)
lb.writeln("> Bound to station xbee/ buffer")

onHold = False

def data_callback(xbee_message):
    #print(xbee_message.data.decode())
    rb.writeln(xbee_message.data.decode())
    #global onHold
    #onHold = False

def main():
    global onHold
    try:
        device.open()

        #print("> Trying to find", remote_id, end="")
        lb.writeln("> Trying to find " + str(remote_id))
        xbee_network = device.get_network()
        remote_device = xbee_network.discover_device(remote_id)

        if remote_device is None:
            #print(" ...could not find", remote_id)
            lb.writeln("> Could not find " + str(remote_id))
            exit(1)

        #print(" ...found", remote_id)
        lb.writeln("> " + str(remote_id) + " found")
        device.add_data_received_callback(data_callback)
        device.set_sync_ops_timeout(100)

        #print("> RoboShell online")
        lb.writeln("> RoboShell online")
        rb.writeln("OUTPUT")

        while True:
            if not onHold:
                #outgoing_data = input("> RoboShell:$ ")
                outgoing_data = lb.input("> RoboShell:$ ")

                #Custom command catching
                if outgoing_data.strip().lower() == "exit":
                    #print('> Closing xbee connection')
                    lb.writeln("> Closing xbee connection")
                    device.close()
                    #print("> Closing RoboShell")
                    lb.writeln("> Closing RoboShell")
                    exit(1)
                else:
                    #onHold = True
                    device.send_data(remote_device, outgoing_data)

    finally:
        if device is not None and device.is_open():
            device.close()
            print('\n> Closed xbee connection')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        left_window.endwin()
        right_window.endwin()
        print("> Closing RoboShell")
