from Domoticz import Log, Error, Debug
import Domoticz
from .device_types import device_types, get_typedef


def subscribe_topics(mqttConn):
    topics = []

    for cc in device_types:
        for device_type in device_types[cc]:
            special_topic = get_typedef(cc, device_type).get("topic")
            topic = "zwave/+{}+/{}".format(cc, device_type) if special_topic is None else "zwave/+{}+/{}".format(cc, special_topic)
            topics.append(
                {"Topic": topic, "QoS": 0},
            )
    Domoticz.Debug("Subscribed topics: {}".format(topics))
    mqttConn.Send({"Verb": "SUBSCRIBE", "PacketIdentifier": 1001, "Topics": topics})
