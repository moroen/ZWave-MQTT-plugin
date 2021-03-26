# Basic Python Plugin Example
#
# Author: GizMoCuz
#
"""
<plugin key="BasePlug" name="ZWave-MQTT" author="moroen" version="0.0.1" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://www.google.com/">
    <description>
        <h2>Zwave MQTT</h2><br/>
        Overview...
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Feature one...</li>
            <li>Feature two...</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>Device Type - What it does...</li>
        </ul>
        <h3>Configuration</h3>
        Configuration options...
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="test.mosquitto.org"/>
        <param field="Port" label="Connection" required="true" width="200px">
            <options>
                <option label="Unencrypted" value="1883" default="true" />
                <option label="Encrypted" value="8883" />
                <option label="Encrypted (Client Certificate)" value="8884" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz

# from Domoticz import Devices, Parameters

import json

import cclass

class mqtt_device:
    pass


class BasePlugin:
    enabled = False
    mqttConn = None
    mqtt_devices = {}
    mqtt_unit_map = {}

    def __init__(self):
        # self.var = 123
        self.counter = 0
        return

    def indexRegisteredDevices(self):
        if len(Devices) > 0:
            # Some devices are already defined

            for aUnit in Devices:
                dev_id = Devices[aUnit].DeviceID

                self.updateDevice(aUnit)
                self.mqtt_unit_map[dev_id] = aUnit

            print(self.mqtt_unit_map)
            return [dev.DeviceID for key, dev in Devices.items()]
        else:
            deviceID = [-1]
            return deviceID

    def registerDevice(self, device_id):
    
        if device_id not in self.mqtt_devices:
            new_unit_id = firstFree()

            Domoticz.Device(
                Name=device_id,
                Unit=new_unit_id,
                Type=244,
                Subtype=73,
                Switchtype=7,
                DeviceID=device_id,
            ).Create()

            # Map the added device
            self.mqtt_devices.append(device_id)
            self.mqtt_unit_map[device_id] = new_unit_id

    def updateDevice(self, Unit):
        pass

    def onStart(self):
        Domoticz.Log("onStart called")

        Domoticz.Debugging(1)

        self.mqtt_devices = self.indexRegisteredDevices()

        self.mqttConn = Domoticz.Connection(
            Name="MQTT Test",
            Transport="TCP/IP",
            Protocol="MQTT",
            Address=Parameters["Address"],
            Port=Parameters["Port"],
        )
        self.mqttConn.Connect()

        # self.registerDevices()

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")
        if Status == 0:
            Domoticz.Debug("MQTT connected successfully.")
            sendData = {"Verb": "CONNECT", "ID": "645364363"}
            Connection.Send(sendData)
        else:
            Domoticz.Log(
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
        Domoticz.Log("onMessage called")
        DumpDictionaryToLog(Data)

        if Data["Verb"] == "CONNACK":
            Domoticz.Log("Connection accepted")
            self.mqttConn.Send(
                {
                    "Verb": "SUBSCRIBE",
                    "PacketIdentifier": 1001,
                    "Topics": [
                        {"Topic": "zwave/+/38/#", "QoS": 0},
                        {"Topic": "zwave/+/+/38/#", "QoS": 0},
                    ],
                }
            )
        elif Data["Verb"] == "PUBLISH":
            i = Data["Topic"].find("currentValue")

            if i > -1:
                device = Data["Topic"][0:i - 1]
                self.registerDevice(device)

                print("Update")
                print(self.mqtt_unit_map)
                unit = self.mqtt_unit_map[device]
                print(unit)

                payload = json.loads(Data["Payload"].decode("utf-8"))
                
                if cclass.multilevel_switch in device:
                    nValue = 2 if payload["value"] > 0 else 0
                    sValue = str(payload["value"])
                    Devices[unit].Update(nValue=nValue, sValue=sValue)

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log(
            "onCommand called for Unit "
            + str(Unit)
            + ": Parameter '"
            + str(Command)
            + "', Level: "
            + str(Level)
        )

        if Command == "On":
            Domoticz.Log("Command - On")
            self.mqttConn.Send(
                {
                    "Verb": "PUBLISH",
                    "QoS": 1,
                    "PacketIdentifier": 1001,
                    "Topic": "{}/targetValue/set".format(Devices[Unit].DeviceID),
                    "Payload": '{{"value": {}}}'.format(Level),
                }
            )
        elif Command == "Off":
            Domoticz.Log("Command - Off")
            self.mqttConn.Send(
                {
                    "Verb": "PUBLISH",
                    "QoS": 1,
                    "PacketIdentifier": 1001,
                    "Topic": "{}/targetValue/set".format(Devices[Unit].DeviceID),
                    "Payload": '{"value": 0}',
                }
            )
        elif Command == "Set Level":
            payload = '{{"value": {}}}'.format(Level)
            self.mqttConn.Send(
                {
                    "Verb": "PUBLISH",
                    "QoS": 1,
                    "PacketIdentifier": 1001,
                    "Topic": "{}/targetValue/set".format(Devices[Unit].DeviceID),
                    "Payload": payload,
                }
            )

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log(
            "Notification: "
            + Name
            + ","
            + Subject
            + ","
            + Text
            + ","
            + Status
            + ","
            + str(Priority)
            + ","
            + Sound
            + ","
            + ImageFile
        )

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")

        if self.counter == 6:
            Domoticz.Log("Sending PING")
            self.mqttConn.Send({"Verb": "PING"})
            self.counter = 0
        else:
            self.counter = self.counter + 1


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
def firstFree():
    for num in range(1, 250):
        if num not in Devices:
            return num
    return


def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
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
                Domoticz.Log(Depth+"> Dict '"+x+"' ("+str(len(theDict[x]))+"):")
                DumpDictionaryToLog(theDict[x], Depth+"---")
            elif isinstance(theDict[x], list):
                Domoticz.Log(Depth+"> List '"+x+"' ("+str(len(theDict[x]))+"):")
                DumpListToLog(theDict[x], Depth+"---")
            elif isinstance(theDict[x], str):
                Domoticz.Log(Depth+">'" + x + "':'" + str(theDict[x]) + "'")
            else:
                Domoticz.Log(Depth+">'" + x + "': " + str(theDict[x]))

def DumpListToLog(theList, Depth):
    if isinstance(theList, list):
        for x in theList:
            if isinstance(x, dict):
                Domoticz.Log(Depth+"> Dict ("+str(len(x))+"):")
                DumpDictionaryToLog(x, Depth+"---")
            elif isinstance(x, list):
                Domoticz.Log(Depth+"> List ("+str(len(theList))+"):")
                DumpListToLog(x, Depth+"---")
            elif isinstance(x, str):
                Domoticz.Log(Depth+">'" + x + "':'" + str(theList[x]) + "'")
            else:
                Domoticz.Log(Depth+">'" + x + "': " + str(theList[x]))

