# Plugin for using zwavejs2mqtt as a zwave interface
#
# Author: moroen
#
"""
<plugin key="BasePlug" name="ZWave-MQTT" author="moroen" version="0.0.1" wikilink="https://github.com/moroen/ZWave-MQTT-plugin/wiki" externallink="https://github.com/moroen/ZWave-MQTT-plugin">
    <description>
        <h2>Zwave MQTT</h2><br/>
    </description>
    <params>
        <param field="Address" label="Broker Address" width="200px" required="true" default="test.mosquitto.org"/>
        <param field="Port" label="Connection" required="true" width="200px">
            <options>
                <option label="Unencrypted" value="1883" default="true" />
                <option label="Encrypted" value="8883" />
                <option label="Encrypted (Client Certificate)" value="8884" />
            </options>
        </param>

        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz

# from Domoticz import Devices, Parameters

import importlib

import json

from uuid import getnode
import api.devices


class mqtt_device:
    pass


class BasePlugin:
    enabled = False
    mqttConn = None
    # mqtt_devices = {}
    mqtt_unit_map = {}

    def __init__(self):
        # self.var = 123
        self.counter = 0
        return

    def onStart(self):
        Domoticz.Log("onStart called")

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
            
        api.devices.indexRegisteredDevices(self, Devices)

        self.mqttConn = Domoticz.Connection(
            Name="MQTT Test",
            Transport="TCP/IP",
            Protocol="MQTT",
            Address=Parameters["Address"],
            Port=Parameters["Port"],
        )
        self.mqttConn.Connect()

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        # Domoticz.Log("onConnect called")
        if Status == 0:
            Domoticz.Debug("MQTT connected successfully.")
            new_id = getnode()
            print("Connecting with nodeid: {}".format(new_id))
            sendData = {"Verb": "CONNECT", "ID": new_id}
            Connection.Send(sendData)
        else:
            Domoticz.Error(
                "Failed to connect ("
                + str(Status)
                + ") to: "
                + Parameters["Address"]
                + ":"
                + Parameters["Port"]
                + " with error: "
                + Description
            )

    def onMessage(self, Connection, Data):
        # Domoticz.Log("onMessage called")
        # DumpDictionaryToLog(Data)

        importlib.reload(api)

        if Data["Verb"] == "CONNACK":
            Domoticz.Debug("MQTT Connection accepted")
            self.mqttConn.Send(
                {
                    "Verb": "SUBSCRIBE",
                    "PacketIdentifier": 1001,
                    "Topics": [
                        {"Topic": "zwave/+/38/+/currentValue", "QoS": 0},
                        {"Topic": "zwave/+/+/38/+/currentValue", "QoS": 0},
                        {"Topic": "zwave/+/37/+/currentValue", "QoS": 0},
                        {"Topic": "zwave/+/+/37/+/currentValue", "QoS": 0},
                        {"Topic": "zwave/+/+/48/#", "QoS": 0},
                        {"Topic": "zwave/+/48/#", "QoS": 0},
                        {"Topic": "zwave/+/+/49/#", "QoS": 0},
                        {"Topic": "zwave/+/49/#", "QoS": 0},
                        {"Topic": "zwave/+/+/67/+/setpoint/+", "QoS": 0},
                        {"Topic": "zwave/+/67/+/setpoint/+", "QoS": 0},
                        {"Topic": "zwave/+/+/91/#", "QoS": 0},
                        {"Topic": "zwave/+/91/#", "QoS": 0},
                        {"Topic": "zwave/+/+/50/#", "QoS": 0},
                        {"Topic": "zwave/+/50/#", "QoS": 0},
                    ],
                }
            )
        elif Data["Verb"] == "PUBLISH":

            device, command_class, device_type, payload = api.devices.parse_topic(
                Data["Topic"], Data["Payload"]
            )
            # device, device_type = api.devices.find_device_and_type(Data["Topic"])
            # payload = json.loads(Data["Payload"].decode("utf-8"))

            # print(
            #     "Device: {}\nCommand_class: {}\nType: {}\nPayload: {}\n".format(
            #         device, command_class, device_type, payload
            #     )
            # )

            # if Data["Topic"][-4:] == "/set":
            #     # Ingnore all set messages, the update should come from the result messages
            #     return

            if device is not None:
                if device not in self.mqtt_unit_map:
                    if not api.devices.registerDevice(
                        self, Data["Topic"], self.firstFree()
                    ):
                        # Unable to register the new device, ignore
                        return

                api.devices.updateDevice(self, Devices, Data["Topic"], Data["Payload"])

    def onCommand(self, Unit, Command, Level, Hue):
        # Domoticz.Log(
        #     "onCommand called for Unit "
        #     + str(Unit)
        #     + ": Parameter '"
        #     + str(Command)
        #     + "', Level: "
        #     + str(Level)
        # )

        importlib.reload(api.devices)
        api.devices.OnCommand(
            self.mqttConn, Devices[Unit].DeviceID, Command, Level, Hue
        )

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        # Domoticz.Log(
        #     "Notification: "
        #     + Name
        #     + ","
        #     + Subject
        #     + ","
        #     + Text
        #     + ","
        #     + Status
        #     + ","
        #     + str(Priority)
        #     + ","
        #     + Sound
        #     + ","
        #     + ImageFile
        # )
        pass

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        # Domoticz.Log("onHeartbeat called")

        if self.counter == 6:
            # Domoticz.Log("Sending PING")
            self.mqttConn.Send({"Verb": "PING"})
            self.counter = 0
        else:
            self.counter = self.counter + 1

    def firstFree(self):
        for num in range(1, 250):
            if num not in Devices:
                return num
        return


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)


def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


# Generic helper functions


def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return


def DumpDictionaryToLog(theDict, Depth=""):
    if isinstance(theDict, dict):
        for x in theDict:
            if isinstance(theDict[x], dict):
                Domoticz.Log(
                    Depth + "> Dict '" + x + "' (" + str(len(theDict[x])) + "):"
                )
                DumpDictionaryToLog(theDict[x], Depth + "---")
            elif isinstance(theDict[x], list):
                Domoticz.Log(
                    Depth + "> List '" + x + "' (" + str(len(theDict[x])) + "):"
                )
                DumpListToLog(theDict[x], Depth + "---")
            elif isinstance(theDict[x], str):
                Domoticz.Log(Depth + ">'" + x + "':'" + str(theDict[x]) + "'")
            else:
                Domoticz.Log(Depth + ">'" + x + "': " + str(theDict[x]))


def DumpListToLog(theList, Depth):
    if isinstance(theList, list):
        for x in theList:
            if isinstance(x, dict):
                Domoticz.Log(Depth + "> Dict (" + str(len(x)) + "):")
                DumpDictionaryToLog(x, Depth + "---")
            elif isinstance(x, list):
                Domoticz.Log(Depth + "> List (" + str(len(theList)) + "):")
                DumpListToLog(x, Depth + "---")
            elif isinstance(x, str):
                Domoticz.Log(Depth + ">'" + x + "':'" + str(theList[x]) + "'")
            else:
                Domoticz.Log(Depth + ">'" + x + "': " + str(theList[x]))
