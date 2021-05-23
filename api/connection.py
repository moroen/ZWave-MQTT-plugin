from Domoticz import Debug
from .device_types import get_device_types, get_typedef
from json import dumps

def subscribe_topics(mqttConn):

    print("Buhu")
    
    device_types = get_device_types()

    topics = []

    for cc in device_types:
        for device_type in device_types[cc]:
            type_def = get_typedef(cc, device_type)

            if type_def.get("Enabled"):
                special_topic = type_def.get("topic")
                topic = (
                    "zwave/+{}+/{}".format(cc, device_type)
                    if special_topic is None
                    else "zwave/+{}+/{}".format(cc, special_topic)
                )
                topics.append(
                    {"Topic": topic, "QoS": 0},
                )

    Debug("Subscribed topics: \n{}".format(dumps(topics, indent=4)))
    mqttConn.Send({"Verb": "SUBSCRIBE", "PacketIdentifier": 1001, "Topics": topics})