from .cclass import multilevel_switch, binary_switch, scene_controller


def OnCommand(mqttConn, DeviceID, Command, Level=None, Hue=None):
    payload = ""

    if scene_controller in DeviceID:
        # Scene controllers are handeled internaly
        print("Scene Controller clicked")
        return

    if Command == "On":
        if multilevel_switch in DeviceID:
            payload = '{{"value": {}}}'.format(255)
        elif binary_switch in DeviceID:
            payload = '{{"value": true}'

    elif Command == "Off":
        if multilevel_switch in DeviceID:
            payload = '{"value": 0}'
        elif binary_switch in DeviceID:
            payload = '{"value": false}'

    elif Command == "Set Level":
        if multilevel_switch in DeviceID:
            payload = '{{"value": {}}}'.format(Level)

    mqttConn.Send(
        {
            "Verb": "PUBLISH",
            "QoS": 1,
            "PacketIdentifier": 1001,
            "Topic": "{}/targetValue/set".format(DeviceID),
            "Payload": payload,
        }
    )
