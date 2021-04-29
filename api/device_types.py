from Domoticz import Log, Error

# Command classes
binary_switch = "/37/"
multilevel_switch = "/38/"
binary_sensor = "/48/"
multilevel_sensor = "/49/"
thermostat = "/67/"
scene_controller = "/91/"
notification = "/113/"

meter = "/50/"
meter_usage = "value/66049"
meter_usage_acummulated = "value/65537"
meter_usage_volt = "value/66561"
meter_usage_ampere = "value/66817"

device_types = {}

# nValue 0: Always 0
# nValue 1: 0 when value == 0 else 1
# nValue 2: 0 when value == 0 else 2
# nValue value: Set nValue to int of value
# sValue 'value' string of value
# sValue 'OnOff' "On" if value > 0 else "Off"
# sValue 'value;' set first part of multipart string to value
# sValue ';value' set second part of multipart string to value

device_types[multilevel_switch] = {
    "currentValue": {
        "Type": "Dimmer",
        "nValue": 2,
        "sValue": "value",
        "state_topic": "targetValue/set",
    }
}
device_types[binary_switch] = {
    "currentValue": {
        "Type": "Switch",
        "nValue": 1,
        "sValue": "OnOff",
        "state_topic": "targetValue/set",
    }
}

device_types[binary_sensor] = {
    "Any": {"Type": "Switch", "nValue": 1, "sValue": "OnOff"},
    "Door-Window": {
        "Type": "DeviceType",
        "DeviceType": 244,
        "SubType": 73,
        "SwitchType": 11,
        "nValue": 1,
        "sValue": "OnOff",
    },
    "Motion": {
        "Type": "DeviceType",
        "DeviceType": 244,
        "SubType": 62,
        "SwitchType": 8,
        "nValue": 1,
        "sValue": "OnOff",
    },
}

device_types[notification] = {
    "Smoke_Alarm/Sensor_status": {
        "Type": "DeviceType",
        "DeviceType": 244,
        "SubType": 62,
        "SwitchType": 5,
        "nValue": 1,
        "sValue": "OnOff",
    },
    "Smoke_Alarm/Alarm_status": {
        "Type": "DeviceType",
        "DeviceType": 244,
        "SubType": 62,
        "SwitchType": 5,
        "nValue": 1,
        "sValue": "OnOff"
        #    },
        #    "Door_state": {
        #        "Type": "DeviceType",
        #        "DeviceType": 244,
        #        "SubType": 73,
        #        "SwitchType": 11,
        #        "nValue": 1,
        #        "sValue": "OnOff"
    },
}


device_types[thermostat] = {
    "setpoint/1": {
        "Type": "DeviceType",
        "DeviceType": 242,
        "SubType": 1,
        "SwitchType": 0,
        "nValue": 0,
        "sValue": "value",
        "factor": 1,
    },
    "setpoint/11": {
        "Type": "DeviceType",
        "DeviceType": 242,
        "SubType": 1,
        "SwitchType": 0,
        "nValue": 0,
        "sValue": "value",
        "factor": 1,
    },
}

device_types[multilevel_sensor] = {
    "Illuminance": {
        "Type": "Illumination",
        "nValue": 0,
        "sValue": "value",
        "factor": 1,
    },
    "Power": {"Type": "Usage", "nValue": 0, "sValue": "value", "factor": 1},
    "Humidity": {
        "Type": "Humidity",
        "nValue": "value",
        "sValue": "humidity_level",
        "factor": 1,
    },
    "Air_temperature": {
        "Type": "Temperature",
        "nValue": 0,
        "sValue": "value",
        "factor": 1,
    },
    "Humidity_combined": {
        "Type": "Temp+Hum",
        "nValue": 0,
        "sValue": ";value;hum",
        "factor": 1,
    },
    "Air_temperature_combined": {
        "Type": "Temp+Hum",
        "nValue": 0,
        "sValue": "value;",
        "factor": 1,
    },
}

device_types[meter] = {
    meter_usage: {"Type": "kWh", "nValue": 0, "sValue": "value;", "factor": 1},
    meter_usage_acummulated: {
        "Type": "kWh",
        "nValue": 0,
        "sValue": ";value",
        "factor": 1000,
    },
    meter_usage_ampere: {
        "Type": "Current (Single)",
        "nValue": 0,
        "sValue": "value",
        "factor": 1,
    },
    meter_usage_volt: {"Type": "Voltage", "nValue": 0, "sValue": "value", "factor": 1},
}

device_types[scene_controller] = {
    "scene": {
        "Type": "DeviceType",
        "DeviceType": 244,
        "SubType": 62,
        "SwitchType": 9,
        "nValue": 1,
        "sValue": "OnOff",
    }
}


def get_typedef(command_class, device_type):
    c_class = device_types.get(command_class)

    if c_class is None:
        Error(
            "Command Class {} with type {} is unknown".format(
                command_class, device_type
            )
        )
        return

    typedef = c_class.get(device_type)
    if typedef is None:
        Error(
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
