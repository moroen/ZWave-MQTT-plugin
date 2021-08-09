# Plugin for using zwavejs2mqtt as a zwave interface
#
# Author: moroen (https://github.com/moroen) & heggink (https://github.com/heggink)
#
"""
<plugin key="ZWave-MQTT" name="ZWave-MQTT version 0.0.1" author="moroen / heggink" version="0.0.1" wikilink="https://github.com/moroen/ZWave-MQTT-plugin/wiki" externallink="https://github.com/moroen/ZWave-MQTT-plugin">
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
        <param field="Username" label="MQTT Username (optional)" width="300px" required="false" default=""/>
        <param field="Password" label="MQTT Password (optional)" width="300px" required="false" default="" password="true"/>
        <param field="Mode5" label="Purge disabled devices" width="150px">
            <options>
                <option label="No" value="0" default="true" />
                <option label="Yes" value="1"/>
            </options>
        </param>

        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Python" value="18"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""

# Get full import path
import site

site.main()

import Domoticz

# from Domoticz import Devices, Parameters

import importlib

import json

from uuid import getnode
import api.devices
from api.connection import subscribe_topics, connect_to_broker
from api.config import set_config_location

from os.path import dirname


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

    def sendMessage(self, msg):
        if self.mqttConn.Connected():
            self.mqttConn.Send(msg)
        else:
            if (
                not self.mqttConn.Connecting()
            ):  # not connected and not connecting so put msg in the queue and connect
                self.messageQueue.append(msg)
                self.mqttConn.Connect()

    def onStart(self):
        Domoticz.Debug("onStart called")

        set_config_location(dirname(__file__))

        if Parameters["Mode6"] != "0":
            try:
                Domoticz.Debugging(int(Parameters["Mode6"]))
            except ValueError:
                Domoticz.Log("Illegal value for Debug, using default (0)")

        api.device_types.get_device_types()

        try:
            if Parameters["Mode5"] == "1":
                from api.commands import purge_disabled_devices

                purge_disabled_devices(Devices)
        except ValueError:
            Debug("Illegal value for Purge, using default (No)")

        api.devices.indexRegisteredDevices(self, Devices)

        self.messageQueue = []

        connect_to_broker(self, address=Parameters["Address"], port=Parameters["Port"])

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        # Domoticz.Log("onConnect called")
        if Status == 0:
            Domoticz.Debug("MQTT connected successfully.")
            sendData = {"Verb": "CONNECT", "ID": "zwave-{}".format(getnode())}
            Connection.Send(sendData)
            while len(self.messageQueue) > 0:
                #                sendMessage(self.messageQueue.pop(0))  # send out all messages queued
                if self.mqttConn.Connected():
                    self.mqttConn.Send(msg)
                else:
                    if (
                        not self.mqttConn.Connecting()
                    ):  # not connected and not connecting so put msg in the queue and connect
                        self.messageQueue.append(msg)
                        self.mqttConn.Connect()

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

        Domoticz.Debug("onMessage called: Verb: {}".format(Data["Verb"]))

        if Data["Verb"] == "CONNACK":
            Domoticz.Debug("MQTT Connection accepted")
            subscribe_topics(self.mqttConn)
        elif Data["Verb"] == "SUBACK":
            pass
        elif Data["Verb"] == "PUBLISH":
            api.devices.onMessage(self, Devices, Data)

    def onCommand(self, Unit, Command, Level, Hue):
        # Domoticz.Log(
        #     "onCommand called for Unit "
        #     + str(Unit)
        #     + ": Parameter '"
        #     + str(Command)
        #     + "', Level: "
        #     + str(Level)
        # )

        api.devices.OnCommand(self, Devices[Unit].DeviceID, Command, Level, Hue)

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
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")

        if self.mqttConn.Connected():
            if self.counter == 3:
                self.mqttConn.Send({"Verb": "PING"})
                self.counter = 0
            else:
                self.counter = self.counter + 1
        else:
            if not self.mqttConn.Connecting():
                self.mqttConn.Connect()

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
