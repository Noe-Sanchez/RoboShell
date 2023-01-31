#!/usr/bin/env python3
import subprocess
import sys
import os
from digi.xbee.devices import XBeeDevice, TimeoutException

#Print usage
if len(sys.argv) < 2:
    "Not enough arguments\n\nUsage:\n\npython3 roboshell_host.py XBEE_PORT\n"
xbee_port = sys.argv[1]
remote_id = "STATION_XBEE"

#Get os-dependant path
wd = os.getcwd()
remote_device = 0

device = XBeeDevice(xbee_port, 9600)
device.set_sync_ops_timeout(5)
print("Bound to boat xbee")

#Main function for data_processing
def data_callback(xbee_message):
    global wd
    global remote_device
    data = xbee_message.data.decode().replace("°","<")
    print("Received command '", data, "'")
    try:
        data_list = list(map(str.strip, data.split()))
        print(data_list)
        
        if data_list[0] == 'cd':
            try:
                data_list.pop(0)
                wd = data_list[0]
                device.send_data(remote_device, '\nChdir ok')    
            except IndexError:
                device.send_data(remote_device, wd)    
        elif data_list[0] == 'ash':
            try:
                data_list.pop(0)
                data_list = ['/bin/sh'] + [(" < " + data_list[0])]
                print(data_list)
                subprocess.call(data_list, shell=True)
                device.send_data(remote_device, '\nSent process to sh')    
            except IndexError:
                device.send_data(remote_device, "Index e")    
        elif data_list[0] == 'ser':
            print("ROS command")
            data_list.pop(0)
            ros_cmd = ' '.join(data_list)
            proc = subprocess.Popen(ros_cmd, shell=True, stdout=subprocess.PIPE, cwd=wd)
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                device.send_data(remote_device, line.strip())
        else:
            print("Normal command")
            proc = subprocess.Popen(data, shell=True,stdout=subprocess.PIPE, cwd=wd)
            tmp = proc.stdout.read()
            device.send_data(remote_device, tmp)

    except TimeoutException:
        print("Process startup failed")
        #device.send_data(remote_device, "Command failed")
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
