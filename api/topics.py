try:
    import Domoticz
except ModuleNotFoundError:
    pass

from io import DEFAULT_BUFFER_SIZE
from Domoticz import Debug
from .device_types import (
    multilevel_switch,
    binary_switch,
    multilevel_sensor,
    central_scene,
    scene_activation,
    meter,
    meter_usage,
    meter_usage_acummulated,
    meter_usage_ampere,
    meter_usage_volt,
    get_typedef,
    get_device_types,
    get_humidity_level,
    thermostat,
    notification,
    battery_status,
)

from json import loads, dumps
from re import DOTALL, search, match, compile


def parse_topic(topic, payload=None):
    if payload is not None:

        try:
            payload = loads(payload.decode("utf-8"))
        except ValueError:
            Domoticz.Debug("Payload decode error: {}".format(payload))
            device_id = None
            command_class = None
            device_type = None
            return device_id, command_class, device_type, payload

    try:
        res = search("(\/[0-9]{1,3})(\/[0-9]{2,3}\/)([0-9]{1,2})\/(.*)", topic)

        if res is None:
            Domoticz.Debug("Unparsable topic received: {}".format(topic))
            device_id = None
            command_class = None
            device_type = None
            return device_id, command_class, device_type, payload

        device_id = res.group(0)
        command_class = res.group(2)
        device_type = res.group(4)
    except AttributeError:
        Domoticz.Debug("Unparsable topic received: {}".format(topic))
        return

    if central_scene in topic:
        return device_id, central_scene, "scene", payload

    if scene_activation in topic:
        try:

            if payload is not None:
                keyNum = payload["value"]

                device_id = device_id + "/" + str(keyNum)
                return device_id, scene_activation, "sceneId", payload
            else:
                return device_id, scene_activation, "sceneId", None
        except KeyError:
            device_id = None
            command_class = None
            device_type = None
            return device_id, command_class, device_type, payload
        except TypeError:
            Debug("Type error: {}".format(topic))

    # Combine 65537 (acumulated) and 66049 (usage) into usage
    if meter in topic:
        if meter_usage_acummulated in topic:
            match = search("(\/[0-9]{1,3})(\/[0-9]{2,3}\/)([0-9]{1,2})\/", topic)
            device_id = match.group(0) + meter_usage
            device_type = meter_usage_acummulated

    return device_id, command_class, device_type, payload
