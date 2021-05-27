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

device_types = {}

import yaml


def write_defaults(file_name):
    with open(file_name, "w") as file:
        documents = yaml.dump(device_types, file)


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
        "Primary_device": True,
        "Enabled": True,
    }
}
device_types[binary_switch] = {
    "currentValue": {
        "Type": "Switch",
        "nValue": 1,
        "sValue": "OnOff",
        "state_topic": "targetValue/set",
        "Primary_device": True,
        "Enabled": True,
    }
}

device_types[binary_sensor] = {
    "Any": {
        "Type": "Switch",
        "nValue": 1,
        "sValue": "OnOff",
        "Primary_device": True,
        "Enabled": True,
    },
    "Door-Window": {
        "Type": "DeviceType",
        "DeviceType": 244,
        "SubType": 73,
        "SwitchType": 11,
        "nValue": 1,
        "sValue": "OnOff",
        "Primary_device": True,
        "Enabled": True,
    },
    "Motion": {
        "Type": "DeviceType",
        "DeviceType": 244,
        "SubType": 62,
        "SwitchType": 8,
        "nValue": 1,
        "sValue": "OnOff",
        "Primary_device": True,
        "Enabled": True,
    },
}

device_types[notification] = {
    "Access_Control/Door_state": {
        "Type": "DeviceType",
        "DeviceType": 244,
        "SubType": 73,
        "SwitchType": 11,
        "nValue": 1,
        "sValue": "OnOff",
        "Primary_device": True,
        "Enabled": True,
    },
    "Smoke_Alarm/Sensor_status": {
        "Type": "DeviceType",
        "DeviceType": 244,
        "SubType": 62,
        "SwitchType": 5,
        "nValue": 1,
        "sValue": "OnOff",
        "Primary_device": True,
        "Enabled": True,
    },
    "Smoke_Alarm/Alarm_status": {
        "Type": "DeviceType",
        "DeviceType": 244,
        "SubType": 62,
        "SwitchType": 5,
        "nValue": 1,
        "sValue": "OnOff",
        "Primary_device": True,
        "Enabled": True,
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
        "Primary_device": True,
        "Enabled": True,
    },
    "setpoint/11": {
        "Type": "DeviceType",
        "DeviceType": 242,
        "SubType": 1,
        "SwitchType": 0,
        "nValue": 0,
        "sValue": "value",
        "factor": 1,
        "Primary_device": True,
        "Enabled": True,
    },
}

device_types[multilevel_sensor] = {
    "Illuminance": {
        "Type": "Illumination",
        "nValue": 0,
        "sValue": "value",
        "factor": 1,
        "Primary_device": True,
        "Enabled": True,
    },
    "Power": {
        "Type": "Usage",
        "nValue": 0,
        "sValue": "value",
        "factor": 1,
        "Primary_device": True,
        "Enabled": True,
    },
    "Humidity": {
        "Type": "Humidity",
        "nValue": "value",
        "sValue": "humidity_level",
        "factor": 1,
        "Primary_device": True,
        "Enabled": True,
    },
    "Air_temperature": {
        "Type": "Temperature",
        "nValue": 0,
        "sValue": "value",
        "factor": 1,
        "Primary_device": True,
        "Enabled": True,
    },
    "Humidity_combined": {
        "Type": "Temp+Hum",
        "nValue": 0,
        "sValue": ";value;hum",
        "factor": 1,
        "Primary_device": True,
        "Enabled": True,
    },
    "Air_temperature_combined": {
        "Type": "Temp+Hum",
        "nValue": 0,
        "sValue": "value;",
        "factor": 1,
        "Primary_device": True,
        "Enabled": True,
    },
}

device_types[meter] = {
    meter_usage: {
        "Type": "kWh",
        "nValue": 0,
        "sValue": "value;",
        "factor": 1,
        "Primary_device": True,
        "Enabled": True,
    },
    meter_usage_acummulated: {
        "Type": "kWh",
        "nValue": 0,
        "sValue": ";value",
        "factor": 1000,
        "Primary_device": True,
        "Enabled": True,
    },
    meter_usage_ampere: {
        "Type": "Current (Single)",
        "nValue": 0,
        "sValue": "value",
        "factor": 1,
        "Primary_device": True,
        "Enabled": True,
    },
    meter_usage_volt: {
        "Type": "Voltage",
        "nValue": 0,
        "sValue": "value",
        "factor": 1,
        "Primary_device": True,
        "Enabled": True,
    },
}

device_types[central_scene] = {
    "scene": {
        "Type": "DeviceType",
        "DeviceType": 244,
        "SubType": 62,
        "SwitchType": 9,
        "nValue": 1,
        "sValue": "OnOff",
        "topic": "scene/+",
        "Primary_device": True,
        "Enabled": True,
    }
}

device_types[scene_activation] = {
    "sceneId": {
        "Type": "DeviceType",
        "DeviceType": 244,
        "SubType": 62,
        "SwitchType": 9,
        "nValue": 1,
        "sValue": "OnOff",
        "Primary_device": True,
        "Enabled": True,
    }
}

device_types[battery_status] = {
    "level": {
        "Type": "Battery_Level",
        # "DeviceType": 244,
        # "SubType": 62,
        # "SwitchType": 9,
        # "nValue": 1,
        # "sValue": "OnOff",
        "Primary_device": False,
        "Enabled": True,
    }
}

if __name__ == "__main__":
    # add_default(True)
    # print(device_types)
    write_defaults("device_types.yml")
