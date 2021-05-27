from api.device_types import get_typedef
from re import M, search
import re
from Domoticz import Debug
from .topics import parse_topic


def handle_plugin_command(plugin, Data, Devices):
    Debug("Command received with topic: {}".format(Data["Topic"]))
    print(Data["Topic"])
    match = search("(\/command\/)(\w+)", Data["Topic"])
    if match is not None:
        if match.group(2) == "reconnect":
            do_reconnect()
        elif match.group(2) == "purge":
            purge_disabled_devices(Devices)


def do_reconnect():
    from .connection import reconnect_to_broker
    from .device_types import get_device_types

    get_device_types(reload=True)
    reconnect_to_broker()


def purge_disabled_devices(Devices):
    Debug("Purging disabled devices")
    for unit in list(Devices):
        devID = Devices[unit].DeviceID
        device, command_class, device_type, _ = parse_topic(devID)
        typedef = get_typedef(command_class, device_type)
        if not typedef["Enabled"]:
            Devices[unit].Delete()
