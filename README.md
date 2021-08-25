[![Lint with black](https://github.com/moroen/ZWave-MQTT-plugin/actions/workflows/black.yml/badge.svg)](https://github.com/moroen/ZWave-MQTT-plugin/actions/workflows/black.yml)

# ZWave-MQTT-plugin
A domoticz plugin for zwave over MQTT.
If you are currently using OZW in domoticz:
- You cannot run OZW and zwavejs2mqtt at the same time using the same zwave adapter. You can using different adapters of course.
- Note the OZW key in the OZW hardware section, you'll need it later. 
- Also note the device name of your zwave controller.
- Disable the domoticz  OZW controller in the hardware section.

## Install and run zwavejs2mqtt
The default way:
```
docker run --rm -it -p 8091:8091 -p 3000:3000 --device=/dev/ttyACM0 --mount source=zwavejs2mqtt,target=/usr/src/app/store zwavejs/zwavejs2mqtt:latest
```
Using persistent storage, started on system startup and running in the background (preferred):
create a storage folder: /opt/zwavejs2mqtt/store
```
docker run -d --name zwavejs2mqtt --restart unless-stopped -v /opt/zwavejs2mqtt/store:/usr/src/app/store -p 8091:8091 -p 3000:3000 --device=/dev/ttyACM0  zwavejs/zwavejs2mqtt:latest
```
This will name the container zwavejs2mqtt and allow you to start, stop, inspect, remove, ...
Replace /dev/ttyACM0 with your serial device

## Configure zwavejs2mqtt
Open the browser http://localhost:8091. 
- Zwave configuration: 
    - Select serial port for your controller
    - input the network key from domoticz OZW (notice the difference in format)
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
If you migrate from OZW, this will be a new plugin with new devices. Once you delete OZW in domoticz, your old devices are gone. If you need to retain history then you need to replace the old device (https://www.domoticz.com/wiki/Managing_Devices#Replace_device) with the new one if identical devices are created.
New devices will be (automatically) added to domoticz (new names, new IDX) on the first status change. To add a device to domoticz, toggle the device by any means, like using the zwave control-planel of zwavejs2mqtt. Battery devices need to be woken up. You can also re-interview nodes and, worst case, re-include but that should not be needed.

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

## Clean up
When everything functions currectly, delete the OZW hardware in domoticz. Please note that dzvents does not like multiple devices with the same name even if the hardware is disabled. Once you delete the OZW hardware, best to restart domoticz so all the new device names are picked up correctly. Also good to completely reboot to test total system startup (including zwavejs2mqtt service or docker container).
