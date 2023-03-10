#!/usr/bin/env python3
import subprocess
import sys
import os
from digi.xbee.devices import XBeeDevice, TimeoutException

if len(sys.argv) < 2:
    "Not enough arguments\n\nUsage:\n\npython3 roboshell_host.py XBEE_PORT\n"
xbee_port = sys.argv[1]
remote_id = "STATION_XBEE"

wd = os.getcwd()
remote_device = 0

device = XBeeDevice(xbee_port, 9600)
print("Bound to boat xbee")

def data_callback(xbee_message):
    global wd
    global remote_device
    data = xbee_message.data.decode()
    print("Received command '", data, "'")
    try:
        data_list = list(map(str.strip, data.split()))
        print(data_list)
        '''
        if len(data_list) > 1 and data_list[0] == 'cd':
            if data_list[1] == '..':
                wd = wd.split('/')
                wd.pop()
                wd = '/'.join(wd)
                print(wd)
            else:
                data_list.pop(0)
                wd = data_list[0]
        '''
        if data_list[0] == 'cd':
            try:
                data_list.pop(0)
                wd = data_list[0]
                device.send_data(remote_device, 'Chdir ok')    
            except IndexError:
                device.send_data(remote_device, wd)    
        else:
            proc = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, cwd=wd)
            #tmp = proc.stdout.readlines()
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                device.send_data(remote_device, line.strip())
            #print(tmp)
            #for line in tmp:
    except TimeoutException:
        print("Process startup failed")
        device.send_data(remote_device, "Command failed")
    except Exception as e:
        print("Exception raised:", e)
        device.send_data(remote_device, str(e))
    
def main():
    global remote_device

    try:
        device.open()

        print("Trying to find", remote_id, end="")
        xbee_network = device.get_network()
        remote_device = xbee_network.discover_device(remote_id)

        if remote_device is None:
            print(" ...could not find", remote_id)
            exit(1)

        print(" ...found", remote_id)
        device.add_data_received_callback(data_callback)

        while True:
            pass

    finally:
        if device is not None and device.is_open():
            device.close()
            print('Closed xbee connection')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Closing host")
