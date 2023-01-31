#!/usr/bin/env python
import sys
import curses
from Buffer_class import Buffer
from digi.xbee.devices import XBeeDevice

#Print usage
if len(sys.argv) < 2:
    print("Not enough arguments\n\nUsage:\n\npython3 roboshell_client.py XBEE_PORT\n")
    exit(1)

xbee_port = sys.argv[1]
remote_id = "BOAT_XBEE"

#Start curses and create both windows
w = curses.initscr()
curses.start_color()
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)

#Hard coded size, need an cross platform way of obtaining env size
lines = 42
columns = 60

half_width = int(columns / 2)

left_window = curses.newwin(lines, half_width)
lb = Buffer(left_window, lines)

separator = curses.newwin(lines, 1, 0, half_width + 2)
separator.bkgd(' ', curses.color_pair(1) | curses.A_BOLD)
separator.refresh()

right_window = curses.newwin(lines, half_width, 0, half_width + 5)
rb = Buffer(right_window, lines)


device = XBeeDevice(xbee_port, 9600)
lb.writeln("> Bound to station xbee/ buffer")

#Just print everything the other xbee sends back
def data_callback(xbee_message):
    rb.writeln(xbee_message.data.decode())

def main():
    #Try block for closing xbee serial port in case of crash
    try:
        #Try to connect xbees
        device.open()
        lb.writeln("> Trying to find " + str(remote_id))
        xbee_network = device.get_network()
        remote_device = xbee_network.discover_device(remote_id)

        if remote_device is None:
            lb.writeln("> Could not find " + str(remote_id))
            exit(1)

        lb.writeln("> " + str(remote_id) + " found")
        device.add_data_received_callback(data_callback)
        device.set_sync_ops_timeout(100)

        lb.writeln("> RoboShell online")
        rb.writeln("OUTPUT")

        while True:
            #Command input
            outgoing_data = lb.input("> RoboShell:$ ")

            #Custom command catching
            if outgoing_data.strip().lower() == "exit":
                lb.writeln("> Closing xbee connection")
                device.close()
                lb.writeln("> Closing RoboShell")
                exit(1)
            else:
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
