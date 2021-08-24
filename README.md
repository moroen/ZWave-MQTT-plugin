[![Lint with black](https://github.com/moroen/ZWave-MQTT-plugin/actions/workflows/black.yml/badge.svg)](https://github.com/moroen/ZWave-MQTT-plugin/actions/workflows/black.yml)

# ZWave-MQTT-plugin
A domoticz plugin for zwave over MQTT

## Install and run zwavejs2mqtt
```
docker run --rm -it -p 8091:8091 -p 3000:3000 --device=/dev/ttyACM0 --mount source=zwavejs2mqtt,target=/usr/src/app/store zwavejs/zwavejs2mqtt:latest
```
Replace /dev/ttyACM0 with your serial device

## Configure zwavejs2mqtt
Open the browser http://localhost:8091. 
- Zwave configuration: 
    - Select serial port
- MQTT configuration: 
    - Set the IP (Host URL) of the MQTT broker
    - best to switch OFF the retain flag (otherwise, deleted devices keep reappearing until you manually delete the messages from the broker)
- Gateway configuration: 
    - Use node names instead of numeric nodeIDs: Off
    - Ignore location: On
    - Include Node Info: On 

Note: Specifying node names and locations in zwavejs2mqtt is not required, but recommended. This will generate somewhat sane names of the devices when they are added to domoticz.

Hint: To add all devices at once, enable the plugin in domoticz, and press "Save" in zwavejs2mqtt preferences. This will generate status messages for all devices. 
## Install and configure Zwave-MQTT-plugin
```
$ cd plugins
$ git clone https://github.com/moroen/ZWave-MQTT-plugin.git ZWave-MQTT
$ pip3 install -r requirements.txt
```
Add the ZWave-MQTT plugin to domoticz, and specify the IP of the MQTT broker

## Usage
Devices will be added to domoticz on the first status change. To add a device to domoticz, toggle the device by any other means, like using the zwave control-planel of zwavejs2mqtt. Battery devices need to be woken up. You can also re-interview nodes and, worst case, re-include but that should not be needed.

## Implemented command classes
- 37 Switch binary
- 38 Switch multilevel
- 43 Scene controller with remote
- 48 Sensor binary
- 49 Sensor multilevel
    - Illumination
    - Power (Usage)
    - Humididy
    - Temperature
    - Temp + humidity
- 50 Meter
    - Power (Usage)
    - Power (Accumulated)
    - Electric (Current)
    - Electric (Volt)
- 67 Thermostat (experimental)
    - setpoint/1 (Heat)
    - setpoint/11 (Heat eco)
- 91 Central scene
