#!/usr/bin/env python3

import boto3
import Resources


def EC2Actions(ev):
    instanceId = ev.GetEventObject().GetCellValue(ev.GetRow(),0)
    status = ev.GetEventObject().GetCellValue(ev.GetRow(),6)
    az = ev.GetEventObject().GetCellValue(ev.GetRow(),2)
    regionName = az[:-1]
    instance = Resources.GetInstance(regionName)
    if status == "running":
        Resources.debug_print("Stopping instance {0}".format(instanceId))
        instance.Stop(instanceId)
    elif status == "stopped":
        Resources.debug_print("Starting instance {0}".format(instanceId))
        instance.Start(instanceId)
    else:
        Resources.debug_print("Instance status: {0}".format(status))
