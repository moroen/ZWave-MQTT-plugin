#!/bin/env python3

import paho.mqtt.publish as publish
import argparse

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("id")
    parser.add_argument("cc")
    parser.add_argument("type")
    parser.add_argument("value")
    
    parser.add_argument("--host", dest="host", action="store", required=True)
    parser.add_argument("--port", dest="port", default=1883)

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    unit = args.cc if "/" in args.cc else "{}/0".format(args.cc)

    publish.single("zwave/{}/{}/{}".format(args.id, unit, args.type), payload="{{\"value\":{}}}".format(args.value), hostname=args.host, port=int(args.port))

