from re import M, search
import re
from Domoticz import Debug

def handle_plugin_command(plugin, Data):
    Debug("Command received with topic: {}".format(Data["Topic"]))
    print(Data["Topic"])
    match = search("(\/command\/)(\w+)", Data["Topic"])
    if match is not None:
        if match.group(2) == "reconnect":
            from .connection import reconnect_to_broker
            from .device_types import get_device_types
            get_device_types(reload=True)
            reconnect_to_broker()