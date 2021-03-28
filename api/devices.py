import Domoticz
from .cclass import multilevel_switch, binary_switch, multilevel_sensor, scene_controller

def find_sensor_type(device_id):
    i = device_id.rfind("/")
    return device_id[i+1:] if i > -1 else None

def find_device_id(device_id):
    i = device_id.rfind("/")
    return device_id[:i] if i > -1 else None

def find_device_and_type(device_id):
    if scene_controller in device_id:
        return device_id, "scene"
    else:
        i = device_id.rfind("/")
        return device_id[:i] if i > -1 else None, device_id[i+1:] if i > -1 else None


def indexRegisteredDevices(plugin, Devices):
    if len(Devices) > 0:
        # Some devices are already defined

        for aUnit in Devices:
            dev_id = Devices[aUnit].DeviceID

            # self.updateDevice(aUnit)
            plugin.mqtt_unit_map[dev_id] = aUnit

        # print(plugin.mqtt_unit_map)
        return [dev.DeviceID for key, dev in Devices.items()]
    else:
        deviceID = [-1]
        return deviceID

def registerDevice(plugin, device_id, device_type, new_unit_id):
    Domoticz.Log("Registering device {} with type {}".format(device_id, device_type))
    if multilevel_switch in device_id:
        Domoticz.Device(
            Name=device_id,
            Unit=new_unit_id,
            TypeName="Dimmer",
            # Type=244,
            # Subtype=73,
            # Switchtype=7,
            DeviceID=device_id,
        ).Create()

    elif binary_switch in device_id:
        Domoticz.Device(
            Name=device_id,
            Unit=new_unit_id,
            TypeName="Switch",
            # Type=244,
            # Subtype=73,
            # Switchtype=7,
            DeviceID=device_id,
        ).Create()
    
    elif multilevel_sensor in device_id:
        if device_type == "Illuminance":
            Domoticz.Device(
                Name=device_id,
                Unit=new_unit_id,
                TypeName="Illumination",
                # Type=244,
                # Subtype=73,
                # Switchtype=7,
                DeviceID=device_id,
            ).Create()
        elif device_type == "Power":
            Domoticz.Device(
                Name=device_id,
                Unit=new_unit_id,
                TypeName="Usage",
                # Type=244,
                # Subtype=73,
                # Switchtype=7,
                DeviceID=device_id,
            ).Create()
        else:  # Unknown sensor type
            return False
    elif scene_controller in device_id:
        Domoticz.Device(
            Name=device_id,
            Unit=new_unit_id,
            TypeName="Push On",
            # Type=244,
            # Subtype=73,
            # Switchtype=7,
            DeviceID=device_id,
        ).Create()

    else:
        # Unknown device
        return False

    # Map the added device
    plugin.mqtt_devices.append(device_id)
    plugin.mqtt_unit_map[device_id] = new_unit_id
    return True

def updateDevice(plugin, device, value, Devices):

    unit = plugin.mqtt_unit_map[device]

    if multilevel_switch in device:
        nValue = 2 if value > 0 else 0
        sValue = str(value)
        Devices[unit].Update(nValue=nValue, sValue=sValue)

    elif binary_switch in device:
        nValue = 1 if value else 0
        sValue = "On" if value else "Off"
        Devices[unit].Update(nValue=nValue, sValue=sValue)

    elif multilevel_sensor in device:
        nValue = int(value)
        sValue = str(value)
        Devices[unit].Update(nValue=nValue, sValue=sValue)

    elif scene_controller in device:
        if value is not None:
            nValue = 1
            sValue = "On"
            Devices[unit].Update(nValue=nValue, sValue=sValue)
            