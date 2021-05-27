#!/usr/bin/env python3

import boto3
import threading
import wx
import wx.grid


def debug_print(fargs, *args, **kwargs):
    if False:
        print(fargs, args, kwargs)


def GetBuckets():
    s3client = boto3.client('s3')
    s3resource = boto3.resource('s3')
    result = [['Name', 'Owner', 'Tags']]
    response = s3client.list_buckets()['Buckets']
    for bucket in response:
        bucket_versioning = s3resource.BucketVersioning(bucket['Name'])
        bucket_acl = s3resource.BucketAcl(bucket['Name'])
        bucketTags = s3resource.BucketTagging(bucket['Name']).tag_set
        tags = ""
        for tag in bucketTags:
            tags = tag['Key'] + ":" + tag['Value'] + ";"
        result.append([bucket['Name'], bucket_acl.owner['ID'], tags])
    return result


class GetInstances:

    def __init__(self, region = 'eu-west-1'):
        self.client = boto3.client('ec2', region_name=region)
        self.ec2 = boto3.resource('ec2', region_name=region)

    def ListInstanceData(self):
        result = []
        myInstances = self.client.describe_instances()
        for instanceData in myInstances['Reservations']:
            result.append(instanceData['Instances'][0])
        return result

    def Instance(self, InstanceId):
        return self.ec2.Instance(InstanceId)


def GetInstanceDataEU():
    RegionsEU = ['eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-north-1', 'eu-central-1', 'eu-south-1']
    result = []
    for region in RegionsEU:
        debug_print("Getting", region, "data.")
        try:
            result = result + GetInstances(region).ListInstanceData()
        except:
            debug_print("Error getting", region, "data.")
    return result


def GetInstanceDataUS():
    RegionsUS = ['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2']
    result = []
    for region in RegionsUS:
        debug_print("Getting", region, "data.")
        try:
            result = result + GetInstances(region).ListInstanceData()
        except:
            debug_print("Error getting", region, "data.")
    return result


def GetEC2InstanceData():
    result = [['Id', 'Type', 'AZ', 'Private IP', 'Name', 'State'] ]
    for instance in GetInstanceDataEU():
        record = []
        record.append(instance['InstanceId'])
        record.append(instance['InstanceType'])
        record.append(instance['Placement']['AvailabilityZone'])
        record.append(instance['PrivateIpAddress'])
        for tag in instance['Tags']:
            if tag['Key'] == "Name":
               record.append(tag['Value'])
        record.append(instance['State']['Name'])
        result.append(record)
    return result


def GetUsers():
    iamClient = boto3.client('iam')
    users = iamClient.list_users()
    result = [['Name', 'Id', 'ARN']]
    for user in users['Users']:
        result.append([user['UserName'], user['UserId'],user['Arn']])
    return result


class DataPanel(wx.Panel):
    
    def __init__(self, parent, dataFunction):
        wx.Panel.__init__(self, parent)
        dataGrid = wx.grid.Grid(self)
        colLabels = dataFunction()[0]
        dataGrid.CreateGrid(0, len(colLabels))
        row = -1
        for dataRecord in dataFunction():
            if row == -1:
                for col in range(len(colLabels)):
                    dataGrid.SetColLabelValue(col, colLabels[col])
            else:
                dataGrid.AppendRows()
                col = 0
                for value in dataRecord:
                   dataGrid.SetCellValue(row, col, value)
                   col = col + 1
            row = row + 1
        dataGrid.AutoSize()


class ThreadedPanel(wx.Panel):
    
    def __init__(self, parent, colLabels):
        wx.Panel.__init__(self, parent)
        self.dataGrid = wx.grid.Grid(self)
        self.dataGrid.CreateGrid(0, len(colLabels))
        for col in range(len(colLabels)):
            self.dataGrid.SetColLabelValue(col, colLabels[col])
        self.dataGrid.AutoSize()

    def AppendRow(self, dataRecord):
        self.dataGrid.AppendRows()
        col = 0
        row = self.dataGrid.GetNumberRows() - 1
        for value in dataRecord:
            self.dataGrid.SetCellValue(row, col, value)
            col = col + 1
        self.dataGrid.AutoSize()


class GetInstancesThread(threading.Thread):

    def __init__(self, control):
        threading.Thread.__init__(self)
        self.regions = ['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2',
                        'eu-west-1', 'eu-west-2', 'eu-west-3',
                        'eu-north-1', 'eu-central-1', 'eu-south-1', ]
        self.control = control

    def run(self):
        for regionName in self.regions:
            self.client = boto3.client('ec2', region_name=regionName)
            self.ec2 = boto3.resource('ec2', region_name=regionName)
            try:
                instances = self.client.describe_instances()
                for instanceData in instances['Reservations']:
                    instanceId = instanceData['Instances'][0]['InstanceId']
                    instance = self.ec2.Instance(instanceId)
                    record = []
                    record.append(instanceData['Instances'][0]['InstanceId'])
                    record.append(instanceData['Instances'][0]['InstanceType'])
                    record.append(instanceData['Instances'][0]['Placement']['AvailabilityZone'])
                    record.append(instanceData['Instances'][0]['PrivateIpAddress'])
                    for tag in instanceData['Instances'][0]['Tags']:
                        if tag['Key'] == "Name":
                            record.append(tag['Value'])
                    record.append(instanceData['Instances'][0]['State']['Name'])
                    wx.CallAfter(self.control.AppendRow, record)
            except:
                print("Error getting data from region {0}.".format(regionName))
