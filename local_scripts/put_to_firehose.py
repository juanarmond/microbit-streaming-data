# By Andrew Mulholland - https://github.com/gbaman/microbit-experiments

import serial
import sys
import datetime
import boto3
import json

# import re
from serial.tools.list_ports import comports as list_serial_ports

client = boto3.client("firehose")


def put_record(data):
    # data = json.dumps(data) + "\n"
    response = client.put_record(
        DeliveryStreamName="firehose-develop-raw-delivery-stream",
        Record={"Data": data},
    )
    print(data)
    return response


def guess_port():
    """
    From https://github.com/ntoll/microrepl
    Returns the port for the first micro:bit found connected to the computer
    running this script. If no micro:bit is found, returns None.
    """
    ports = list_serial_ports()
    platform = sys.platform
    if platform.startswith("linux"):
        for port in ports:
            if "VID:PID=0D28:0204" in port[2].upper():
                return port[0]
    elif platform.startswith("darwin"):
        for port in ports:
            if "VID:PID=0D28:0204" in port[2].upper():
                return port[0]
    elif platform.startswith("win"):
        for port in ports:
            if "VID:PID=0D28:0204" in port[2].upper():
                return port[0]
    return None


# def get_key_value(line):
#     if ':' in line:
#         key = line.split(":")[0].strip()
#         value = float(line.split(":")[1].strip())
#     else:
#         key = re.sub("[0-9]", "", line)
#         value = float(re.sub("[^0-9]", "", line))
#     line_list = [key, value]
#     # print(line_list)
#     return line_list


def main():
    event = {}
    # event = {"time":"","serial":"","signal":"","x":"","y":"","z":"","distance":"","speed":"","sensor":"","light":"","compass":"","sound":"","temperature":"","tembo":"","magnetic":""}
    try:
        port = guess_port()
        if port == None:
            print("No micro:bit detected!")
            sys.exit(1)
        ser = serial.Serial(port, baudrate=115200, timeout=None)
        ser.flushInput()
        ser.flushOutput()
        print("Micro:bit connected and reading data from it.")
        print("Streaming data events to AWS.")
        while True:
            ct = datetime.datetime.now()
            ts = ct.timestamp()
            event["event_timestamp"] = ts

            line = ser.readline().decode().rstrip()

            try:
                dic = json.loads(line)
                full_event = event | dic
                # print(full_event)
                put_record(full_event)
            except:
                print("ERROR JSON", [line])

    finally:
        try:
            ser.close()
            # print(event)
        except UnboundLocalError:
            pass


main()
