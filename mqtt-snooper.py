#!/bin/env python3

import paho.mqtt.client as mqtt
import argparse
import api.devices

_translate = False

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("zwave/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if _translate:
        dev, devtype = api.devices.find_device_and_type(msg.topic)
        print("{} -> {}".format(dev, devtype))


def mqtt_snooper(ip):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(ip, 1883, 60)
    return client

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("IP")

    parser.add_argument("-t", dest="translate", action="store_true")

    return parser.parse_args()

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
if __name__ == "__main__":
    args = get_args()
    _translate = args.translate
    mqtt_snooper(str(args.IP)).loop_forever()
