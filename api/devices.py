import Domoticz
from .cclass import multilevel_switch, binary_switch

def indexRegisteredDevices(plugin, Devices):
    if len(Devices) > 0:
        # Some devices are already defined

        for aUnit in Devices:
            dev_id = Devices[aUnit].DeviceID

            # self.updateDevice(aUnit)
            plugin.mqtt_unit_map[dev_id] = aUnit

        print(plugin.mqtt_unit_map)
        return [dev.DeviceID for key, dev in Devices.items()]
    else:
        deviceID = [-1]
        return deviceID

def registerDevice(plugin, device_id, new_unit_id):
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
    

    # Map the added device
    plugin.mqtt_devices.append(device_id)
    plugin.mqtt_unit_map[device_id] = new_unit_id

def updateDevice(self, Unit):
    pass