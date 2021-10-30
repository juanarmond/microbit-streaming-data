# By Andrew Mulholland - https://github.com/gbaman/microbit-experiments

import serial
import sys
import datetime
import boto3
import json
from serial.tools.list_ports import comports as list_serial_ports

client = boto3.client("firehose")


def put_record(event):
    data = json.dumps(event) + "\n"
    response = client.put_record(
        DeliveryStreamName="firehose-develop-raw-delivery-stream",
        Record={"Data": data},
    )
    print(event)
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


def main():
    event = {}
    # data = [["a.x", "a.y", "a.z", "distance", "speed", "sensor"], ]
    try:
        port = guess_port()
        if port == None:
            print("No micro:bit detected!")
            sys.exit(1)
        ser = serial.Serial(port, baudrate=115200)
        print("Micro:bit connected and reading data from it.")
        print("Streaming data events to AWS.")
        while True:
            ct = datetime.datetime.now()
            ts = ct.timestamp()
            event["event_timestamp"] = ts

            line = ser.readline().decode()

            line_list = line.split("\r\n")[0].strip().split(":")
            # print([line],line_list)

            if line_list[0] not in event:
                event[line_list[0]] = line_list[1]
            else:
                # print(event)
                # print('-'*100)
                put_record(event)

    finally:
        try:
            ser.close()
            # print(event)
        except UnboundLocalError:
            pass


main()
