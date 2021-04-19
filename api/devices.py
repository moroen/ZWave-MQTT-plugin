try:
    import Domoticz
except ModuleNotFoundError:
    pass

from typing import NoReturn
from .device_types import (
    multilevel_switch,
    binary_switch,
    multilevel_sensor,
    scene_controller,
    meter,
    meter_usage,
    meter_usage_acummulated,
    meter_usage_ampere,
    meter_usage_volt,
    device_types,
    get_typedef,
    get_humidity_level,
    thermostat
)

from json import loads


def find_sensor_type(device_id):
    i = device_id.rfind("/")
    return device_id[i + 1 :] if i > -1 else None


def find_device_id(device_id):
    i = device_id.rfind("/")
    return device_id[:i] if i > -1 else None


def parse_topic(topic, payload=None):
    if scene_controller in topic:
        return topic, scene_controller, "scene", payload
    elif meter in topic:
        command_class = meter
        i = topic.find("/value")

        if meter_usage_acummulated in topic:
            device_id = topic[: i + 1] + meter_usage
            device_type = meter_usage_acummulated
        else:
            device_id = topic[:i] + topic[i + 6 :] if i > -1 else topic
            device_type = topic[i + 7 :] if i > -1 else None
    elif thermostat in topic:
        
        command_class = thermostat

        device_id = topic
        
        i = topic.find("/setpoint")
        
        device_type = topic[i+1 :] 

    else:
        i = topic.rfind("/")
        device_id = topic[:i] if i > -1 else None
        device_type = topic[i + 1 :] if i > -1 else None

        i = device_id.rfind("/")
        j = device_id.rfind("/", 0, i)

        command_class = device_id[j : i + 1]

    if payload is not None:
        payload = loads(payload.decode("utf-8"))

    return device_id, command_class, device_type, payload


def indexRegisteredDevices(plugin, Devices):
    if len(Devices) > 0:
        # Some devices are already defined

        for aUnit in Devices:
            dev_id = Devices[aUnit].DeviceID

            # self.updateDevice(aUnit)
            plugin.mqtt_unit_map[dev_id] = aUnit

        # print(plugin.mqtt_unit_map)
        # return [dev.DeviceID for key, dev in Devices.items()]
    # else:

    #     return deviceID


def registerDevice(plugin, topic, new_unit_id):

    device_id, command_class, device_type, _ = parse_topic(topic)

    Domoticz.Debug(
        "Registering device {} as unit {} with type {}".format(
            device_id, new_unit_id, device_type
        )
    )

    typedef = get_typedef(command_class, device_type)

    print("Typedef: {}".format(typedef))

    if typedef is not None:
        if typedef["Type"] == "Thermostat":
            Domoticz.Device(
                Name=device_id,
                Unit=new_unit_id,
                Type=242,
                Subtype=1,
                # Switchtype=7,
                DeviceID=device_id,
            ).Create()
        else:
            Domoticz.Device(
                Name=device_id,
                Unit=new_unit_id,
                TypeName=typedef["Type"],
                # Type=244,
                # Subtype=73,
                # Switchtype=7,
                DeviceID=device_id,
            ).Create()

        # Map the added device
        # plugin.mqtt_devices.append(device_id)
        plugin.mqtt_unit_map[device_id] = new_unit_id
        return True
    else:
        return False


def updateDevice(plugin, Devices, topic, mqtt_payload):
    nValue = 0
    sValue = ""

    device_id, command_class, device_type, payload = parse_topic(topic, mqtt_payload)
    unit = plugin.mqtt_unit_map[device_id]
    try:
        sValue = Devices[unit].sValue
    except KeyError:
        # The mapped unit doesn't exist, probably deleted..
        Domoticz.Error(
            "Failed to update device {}, unit {} not found.".format(device_id, unit)
        )
        del plugin.mqtt_unit_map[device_id]
        registerDevice(plugin, topic, plugin.firstFree())
        updateDevice(plugin, Devices, topic, mqtt_payload)
        return

    # Combine TEMP and Humidity if same unit reports both
    if device_type == "Air_temperature" and Devices[unit].Type == 81:
        Domoticz.Debug(
            "Changing unit {} from humidity to Temp+Hum".format(
                unit, device_id, device_type, payload
            )
        )
        sValue = "{};{};{}".format(
            payload["value"],
            Devices[unit].nValue,
            get_humidity_level(Devices[unit].nValue),
        )
        Devices[unit].Update(nValue=0, sValue=sValue, TypeName="Temp+Hum")
        return

    elif device_type == "Humidity" and Devices[unit].Type == 80:
        Domoticz.Debug(
            "Changing unit {} from temperature to Temp+Hum".format(
                unit, device_id, device_type, payload
            )
        )
        sValue = "{};{};{}".format(
            Devices[unit].sValue, payload["value"], get_humidity_level(payload["value"])
        )
        Devices[unit].Update(nValue=0, sValue=sValue, TypeName="Temp+Hum")
        return

    if Devices[unit].Type == 82:  # This is a combined sensor temp + hum sensor
        device_type = "Humidity_combined" if device_type == "Humidity" else device_type
        device_type = (
            "Air_temperature_combined"
            if device_type == "Air_temperature"
            else device_type
        )

    Domoticz.Debug(
        "Updating unit {} as device {} of type {} with {}".format(
            unit, device_id, device_type, payload
        )
    )

    typedef = get_typedef(command_class, device_type)

    if typedef is not None:
        Domoticz.Debug("Updating with typedef: {}".format(typedef))

        if typedef["Type"] == "Scene":
            Devices[unit].Update(nValue=1, sValue="On")
            return

        # nValue
        if typedef["nValue"] == 0:
            nValue = 0
        elif typedef["nValue"] == 1:
            nValue = 0 if payload["value"] == 0 else 1
        elif typedef["nValue"] == 2:
            nValue = 0 if payload["value"] == 0 else 2
        elif typedef["nValue"] == "value":
            nValue = int(payload["value"])

        # sValue
        if typedef["sValue"] == "value":
            sValue = str(payload["value"])
        elif typedef["sValue"] == "value;":
            i = sValue.find(";")
            sValue = (
                str(payload["value"] * typedef["factor"]) + sValue[i:]
                if i > -1
                else sValue
            )

        elif typedef["sValue"] == ";value":
            i = sValue.find(";")
            sValue = (
                sValue[:i] + str(payload["value"] * typedef["factor"])
                if i > -1
                else sValue
            )
        elif typedef["sValue"] == ";value;hum":
            i = sValue.find(";")
            sValue = (
                sValue[:i]
                + ";"
                + str(payload["value"] * typedef["factor"])
                + ";"
                + get_humidity_level(payload["value"])
            )

        elif typedef["sValue"] == "OnOff":
            sValue = "On" if payload["value"] else "Off"
        elif typedef["sValue"] == "humidity_level":
            sValue = get_humidity_level(payload["value"])

        Domoticz.Debug("nValue: {} sValue: {}".format(nValue, sValue))
        Devices[unit].Update(nValue=nValue, sValue=sValue)


def OnCommand(mqttConn, DeviceID, Command, Level=None, Hue=None):
    # device_id, command_class, device_type, payload = parse_topic(DeviceID)
    
    # print(device_id, command_class, device_type)

    payload = None
    topic = None

    print(Command, Level, Hue)

    if scene_controller in DeviceID:
        # Scene controllers are handeled internaly
        # print("Scene Controller clicked")
        return

    if Command == "On":
        topic = "{}/targetValue/set".format(DeviceID)
        if multilevel_switch in DeviceID:
            payload = '{{"value": {}}}'.format(255)
        elif binary_switch in DeviceID:
            payload = '{{"value": true}'

    elif Command == "Off":
        topic = "{}/targetValue/set".format(DeviceID)
        if multilevel_switch in DeviceID:
            payload = '{"value": 0}'
        elif binary_switch in DeviceID:
            payload = '{"value": false}'

    elif Command == "Set Level":
        if multilevel_switch in DeviceID:
            topic = "{}/targetValue/set".format(DeviceID)
            payload = '{{"value": {}}}'.format(Level)
        if thermostat in DeviceID:
            topic = "{}/set".format(DeviceID)
            payload = '{{"value": {}}}'.format(Level)

    mqttConn.Send(
        {
            "Verb": "PUBLISH",
            "QoS": 1,
            "PacketIdentifier": 1001,
            "Topic": topic,
            "Payload": payload,
        }
    )
