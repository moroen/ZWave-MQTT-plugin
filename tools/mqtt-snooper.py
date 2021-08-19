#!/bin/env python3

import paho.mqtt.client as mqtt
import argparse
from datetime import datetime

_clear = False
_topic = "zwave/#"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(_topic)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(
        "{} {} {}".format(
            datetime.now().strftime("%H:%M:%S"), msg.topic, str(msg.payload)
        )
    )

    if _clear:
        print("Clearing topic: {}".format(msg.topic))
        client.publish(msg.topic, payload=None, qos=0, retain=True)


def mqtt_snooper(ip):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(ip, 1883, 60)
    return client


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("IP")
    parser.add_argument("--topic", dest="topic", action="store")
    parser.add_argument("--clear", dest="clear", action="store_true")

    return parser.parse_args()


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
if __name__ == "__main__":
    args = get_args()
    _clear = args.clear

    if args.topic is not None:
        _topic = args.topic

    try:
        mqtt_snooper(str(args.IP)).loop_forever()
    except KeyboardInterrupt:
        quit()