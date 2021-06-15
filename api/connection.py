import Domoticz
from .device_types import get_device_types, get_typedef
from .config import get_mqtt_config
from json import dumps
from os.path import dirname
from yaml import load, FullLoader, dump

_broker_ip = None
_broker_port = None
_plugin = None

def connect_to_broker(plugin, address=None, port=None):
    global _broker_ip, _broker_port, _plugin

    if address is not None:
        _broker_ip = address

    if port is not None:
        _broker_port = port

    _plugin = plugin

    plugin.mqttConn = Domoticz.Connection(
        Name="MQTT Test",
        Transport="TCP/IP",
        Protocol="MQTT",
        Address=_broker_ip,
        Port=_broker_port,
    )
    plugin.mqttConn.Connect()


def reconnect_to_broker():
    Domoticz.Debug("Reconnect called")
    _plugin.mqttConn.Disconnect()
    connect_to_broker(_plugin)


def subscribe_topics(mqttConn):
    topics = []

    device_types = get_device_types()
    conf = get_mqtt_config()

    if conf is not None:

        if device_types is not None:
            for cc in device_types:
                for device_type in device_types[cc]:
                    type_def = get_typedef(cc, device_type)

                    if type_def.get("Enabled"):
                        special_topic = type_def.get("topic")
                        topic = (
                            "{}/+{}+/{}".format(conf["BaseTopic"], cc, device_type)
                            if special_topic is None
                            else "{}/+{}+/{}".format(conf["BaseTopic"], cc, special_topic)
                        )
                        topics.append(
                            {"Topic": topic, "QoS": 0},
                        )
        else:
            Domoticz.Error("No device types defined")

        # Subscribe to command topic
        topics.append({"Topic": "{}-mqtt/#".format(conf["BaseTopic"]), "QoS": 0})

        Domoticz.Debug("Subscribed topics: \n{}".format(dump(topics)))
        mqttConn.Send({"Verb": "SUBSCRIBE", "PacketIdentifier": 1001, "Topics": topics})
    else:
        Domoticz.Error("No configuration, skipping MQTT-Subscribe")