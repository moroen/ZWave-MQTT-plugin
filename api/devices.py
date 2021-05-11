try:
    import Domoticz
except ModuleNotFoundError:
    pass

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
    device_types,
    get_typedef,
    get_humidity_level,
    thermostat,
    notification,
    battery_status,
)

from json import loads
from re import search, match, compile


def find_sensor_type(device_id):
    i = device_id.rfind("/")
    return device_id[i + 1 :] if i > -1 else None


def find_device_id(device_id):
    i = device_id.rfind("/")
    return device_id[:i] if i > -1 else None


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
            keyNum = payload["value"]

            device_id = device_id + "/" + str(keyNum)
            return device_id, scene_activation, "sceneId", payload

        except KeyError:
            device_id = None
            command_class = None
            device_type = None
            return device_id, command_class, device_type, payload

    # Combine 65537 (acumulated) and 66049 (usage) into usage
    if meter in topic:
        if meter_usage_acummulated in topic:
            match = search("(\/[0-9]{1,3})(\/[0-9]{2,3}\/)([0-9]{1,2})\/", topic)
            device_id = match.group(0) + meter_usage
            device_type = meter_usage_acummulated

    return device_id, command_class, device_type, payload


def onMessage(plugin, Devices, Data):
    if Data["Payload"] is not None:
        device, command_class, device_type, payload = parse_topic(
            Data["Topic"], Data["Payload"]
        )

        typedef = get_typedef(command_class, device_type)

        if device is not None:
            if typedef["Primary_device"]:
                if device not in plugin.mqtt_unit_map:
                    if not registerDevice(plugin, Data, plugin.firstFree()):
                        # Unable to register the new primary device, ignore
                        return

                updateDevice(plugin, Devices, Data)
            else:
                # Device Property
                update_device_property(plugin, Devices, Data)


def update_device_property(plugin, Devices, Data):
    Domoticz.Debug(
        "Update_device_property called with topic: {} and payload {}".format(
            Data["Topic"], Data["Payload"]
        )
    )

    device, command_class, device_type, payload = parse_topic(
        Data["Topic"], Data["Payload"]
    )

    typedef = get_typedef(command_class, device_type)

    node_id = match("\/([0-9]{1,3})\/", device).group(1)

    regx = compile("\/{}\/[0-9]{{1,3}}\/[0-9]{{1,2}}".format(node_id))

    for aDevice in plugin.mqtt_unit_map:
        res = regx.match(aDevice)
        if res is not None:
            unit = plugin.mqtt_unit_map[aDevice]
            # For scene activation use Off as value
            # For other devices use the same value
            nValue = (
                0
                if (scene_activation in aDevice or central_scene in aDevice)
                else Devices[unit].nValue
            )
            sValue = (
                "Off"
                if (scene_activation in aDevice or central_scene in aDevice)
                else Devices[unit].sValue
            )

            if typedef["Type"] == "Battery_Level":
                batteryLevel = int(payload["value"])
                Devices[unit].Update(
                    nValue=nValue,
                    sValue=sValue,
                    BatteryLevel=batteryLevel,
                )


def indexRegisteredDevices(plugin, Devices):
    if len(Devices) > 0:
        # Some devices are already defined

        for aUnit in Devices:
            dev_id = Devices[aUnit].DeviceID

            # self.updateDevice(aUnit)
            plugin.mqtt_unit_map[dev_id] = aUnit


def registerDevice(plugin, Data, new_unit_id):

    Domoticz.Debug(
        "registerDevice called with topic: {} and payload {}".format(
            Data["Topic"], Data["Payload"]
        )
    )

    device_id, command_class, device_type, payload = parse_topic(
        Data["Topic"], Data["Payload"]
    )

    typedef = get_typedef(command_class, device_type)

    device_name = device_id

    nodeName = payload.get("nodeName")
    nodeLocation = payload.get("nodeLocation")

    if nodeName is not None:
        if nodeName != "":
            device_name = (
                "{} - {}".format(nodeLocation, nodeName)
                if nodeLocation != ""
                else nodeName
            )

    if typedef is not None:
        if typedef["Primary_device"]:
            if typedef["Type"] == "DeviceType":
                Domoticz.Device(
                    Name=device_name,
                    Unit=new_unit_id,
                    Type=typedef["DeviceType"],
                    Subtype=typedef["SubType"],
                    Switchtype=typedef["SwitchType"],
                    DeviceID=device_id,
                ).Create()
            else:
                Domoticz.Device(
                    Name=device_name,
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
            Domoticz.Log(
                "Registering device {} as unit {} with type {}".format(
                    device_id, new_unit_id, device_type
                )
            )
            return True
        else:
            return False
    else:
        return False


def updateDevice(plugin, Devices, Data):
    nValue = 0
    sValue = ""

    Domoticz.Debug(
        "updateDevice called with topic: {} and payload {}".format(
            Data["Topic"], Data["Payload"]
        )
    )

    device_id, command_class, device_type, payload = parse_topic(
        Data["Topic"], Data["Payload"]
    )
    unit = plugin.mqtt_unit_map[device_id]

    try:
        sValue = Devices[unit].sValue
    except KeyError:
        # The mapped unit doesn't exist, probably deleted..
        Domoticz.Error(
            "Failed to update device {}, unit {} not found.".format(device_id, unit)
        )
        del plugin.mqtt_unit_map[device_id]
        registerDevice(plugin, Data, plugin.firstFree())
        updateDevice(plugin, Devices, Data)
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
        Domoticz.Debug("Changing unit {} from temperature to Temp+Hum".format(unit))
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

        if central_scene in command_class:
            if payload.get("value") is not None:
                # zwavejs2mqtt reports a value if a scene button actually are pressed
                Devices[unit].Update(nValue=1, sValue="On")
            else:
                Domoticz.Debug("Central scene controller with empty value, skipping...")
            return

        if scene_activation in command_class:
            if payload.get("value") is not None:
                # zwavejs2mqtt reports a value if a scene button actually are pressed
                Devices[unit].Update(nValue=1, sValue="On")
            return

        # nValue
        if typedef["nValue"] == 0:
            nValue = 0
        elif typedef["nValue"] == 1:
            if "value" in payload:
                nValue = 0 if payload["value"] == 0 else 1
            else:
                return
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
                else str(payload["value"] * typedef["factor"]) + ";0"
            )

        elif typedef["sValue"] == ";value":
            i = sValue.find(";")
            sValue = (
                sValue[:i] + ";" + str(payload["value"] * typedef["factor"])
                if i > -1
                else "0;" + str(payload["value"])
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
            val = str(payload["value"])
            if val == "True" or val == "22":
                sValue = "On"
                nValue = 1
            else:
                sValue = "Off"
                nValue = 0
        elif typedef["sValue"] == "humidity_level":
            sValue = get_humidity_level(payload["value"])

        Domoticz.Debug("nValue: {} sValue: {}".format(nValue, sValue))
        Devices[unit].Update(nValue=nValue, sValue=sValue)


def OnCommand(plugin, DeviceID, Command, Level=None, Hue=None):
    payload = None
    topic = None

    device_id, command_class, device_type, payload = parse_topic(DeviceID)

    typedef = get_typedef(command_class, device_type)

    if central_scene in DeviceID:
        # Scene controllers are handeled internaly

        return

    if scene_activation in DeviceID:
        # Scene controllers are handeled internaly
        return

    if Command == "On":
        if multilevel_switch in DeviceID:
            payload = '{{"value": {}}}'.format(255)
        elif binary_switch in DeviceID:
            payload = '{{"value": true}'

    elif Command == "Off":
        if multilevel_switch in DeviceID:
            payload = '{"value": 0}'
        elif binary_switch in DeviceID:
            payload = '{"value": false}'

    elif Command == "Set Level":
        payload = '{{"value": {}}}'.format(Level)

    if typedef.get("state_topic") is not None:
        res = search("\/[0-9]{1,3}\/[0-9]{2,3}\/[0-9]{1,2}\/", device_id)
        topic = "zwave{}{}".format(res.group(0), typedef["state_topic"])
    else:
        topic = "zwave{}/set".format(device_id)

    plugin.sendMessage(
        {
            "Verb": "PUBLISH",
            "QoS": 1,
            "PacketIdentifier": 1001,
            "Topic": topic,
            "Payload": payload,
        }
    )
