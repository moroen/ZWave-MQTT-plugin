from Domoticz import Log, Error, Debug
import Domoticz
from .device_types import device_types


def subscribe_topics(mqttConn):
    topics = []

    for cc in device_types:
        for device_type in device_types[cc]:
            topic = "zwave/+{}+/{}".format(cc, device_type)
            topics.append(
                {"Topic": topic, "QoS": 0},
            )
    Domoticz.Debug("Subscribed topics: {}".format(topics))
    mqttConn.Send({"Verb": "SUBSCRIBE", "PacketIdentifier": 1001, "Topics": topics})
