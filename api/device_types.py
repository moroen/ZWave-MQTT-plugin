from typing import Mapping
from Domoticz import Log, Error, Debug
from os.path import dirname, exists
from .utils import merge_dicts

# Command classes
binary_switch = "/37/"
multilevel_switch = "/38/"
scene_activation = "/43/"
binary_sensor = "/48/"
multilevel_sensor = "/49/"
thermostat = "/67/"
central_scene = "/91/"
notification = "/113/"
battery_status = "/128/"

meter = "/50/"
meter_usage = "value/66049"
meter_usage_acummulated = "value/65537"
meter_usage_volt = "value/66561"
meter_usage_ampere = "value/66817"


# nValue 0: Always 0
# nValue 1: 0 when value == 0 else 1
# nValue 2: 0 when value == 0 else 2
# nValue value: Set nValue to int of value
# sValue 'value' string of value
# sValue 'OnOff' "On" if value > 0 else "Off"
# sValue 'value;' set first part of multipart string to value
# sValue ';value' set second part of multipart string to value

_global_device_types_file = "{}/device_types.yml".format(dirname(__file__))
_user_device_types_file = "{}/../user_types.yml".format(dirname(__file__))

_default_device_types = {}
_user_device_types = {}
device_types = {}

def get_device_types(reload=False):
    global device_types, _default_device_types, _user_device_types

    if len(device_types) == 0 or reload:
        from yaml import load, FullLoader
        with open(_global_device_types_file) as file:
            _default_device_types = load(file, FullLoader)

        if exists(_user_device_types_file):
            with open(_user_device_types_file) as file:
                _user_device_types = load(file, FullLoader) 

    device_types = merge_dicts(_default_device_types, _user_device_types)
    return device_types

def get_typedef(command_class, device_type):
    c_class = device_types.get(command_class)

    if c_class is None:
        Log(
            "Command Class {} with type {} is unknown".format(
                command_class, device_type
            )
        )
        return

    typedef = c_class.get(device_type)
    if typedef is None:
        Log(
            "Devicetype {} for command class {} is unknown".format(
                device_type, command_class
            )
        )
        return

    return typedef


def get_humidity_level(humidity):
    if humidity < 35:
        return "2"  # dry
    if humidity > 60:
        return "3"  # wet

    return "1"  # Comfortable

