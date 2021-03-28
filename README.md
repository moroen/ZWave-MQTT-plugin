# ZWave-MQTT-plugin
A domoticz plugin for zwave over MQTT

## Install and run zwavejs2mqtt
```
docker run --rm -it -p 8091:8091 -p 3000:3000 --device=/dev/ttyACM0 --mount source=zwavejs2mqtt,target=/usr/src/app/store zwavejs/zwavejs2mqtt:latest
```
Replace /dev/ttyACM0 with your serial device

## Configure zwavejs2mqtt
Open the browser http://localhost:8091. Select serial port in Zwave configuration. Set the IP (Host URL) of the MQTT broker in MQTT configration. Everything else should be left as default.

## Install and configure Zwave-MQTT-plugin
```
$ cd plugins
$ git clone https://github.com/moroen/ZWave-MQTT-plugin.git ZWave-MQTT
```
Add the ZWave-MQTT plugin to domoticz, and specify the IP of the MQTT broker

## Usage
Devices will be added to domoticz on the first status change. To add a device to domoticz, toggle the device by any other means, like using the zwave control-planel of zwavejs2mqtt

## Implemented command classes
- 37 Switch binary
- 38 Switch multilevel
- 49 Sensor multilevel
    - Illumination
    - Power (Usage)
- 91 Central scene