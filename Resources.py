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


class GetInstance:

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

    def Stop(self, instanceID):
        self.client.stop_instances(InstanceIds=[instanceID])

    def Start(self, instanceID):
        self.client.start_instances(InstanceIds=[instanceID])


def GetSecurityGroups():
    client = boto3.client('ec2')
    resource = boto3.resource('ec2')
    result = [['Id', 'Name', 'Description', 'VPC', 'Tags']]
    for sg in client.describe_security_groups()['SecurityGroups']:
        securityGroup = resource.SecurityGroup(sg['GroupId'])
        tags  = ""
        if securityGroup.tags!=None:
            for tag in securityGroup.tags:
                tags = tag['Key'] + ":" + tag['Value'] + ";"
        result.append([sg['GroupId'], sg['GroupName'], securityGroup.description, securityGroup.vpc_id, tags])
    return result

def GetUsers():
    iamClient = boto3.client('iam')
    users = iamClient.list_users()
    result = [['Id', 'Name', 'ARN']]
    for user in users['Users']:
        result.append([user['UserId'], user['UserName'], user['Arn']])
    return result


class DataPanel(wx.Panel):
    
    def __init__(self, parent, dataFunction):
        wx.Panel.__init__(self, parent)
        self.dataGrid = wx.grid.Grid(self)
        row = -1
        for dataRecord in dataFunction():
            if row == -1:
                colLabels = dataRecord
                self.dataGrid.CreateGrid(0, len(colLabels))
                for col in range(len(colLabels)):
                    self.dataGrid.SetColLabelValue(col, colLabels[col])
            else:
                self.dataGrid.AppendRows()
                col = 0
                for value in dataRecord:
                   self.dataGrid.SetCellValue(row, col, value)
                   col = col + 1
            row = row + 1
        self.dataGrid.AutoSize()


class ThreadedPanel(wx.Panel):
    
    def __init__(self, parent, colLabels):
        wx.Panel.__init__(self, parent)
        self.dataGrid = wx.grid.Grid(self)
        self.dataGrid.EnableEditing(False)
        self.dataGrid.CreateGrid(0, len(colLabels))
        for col in range(len(colLabels)):
            self.dataGrid.SetColLabelValue(col, colLabels[col])
        self.resourcesDict = {}
        self.dataGrid.AutoSize()

    def AppendRow(self, dataRecord):
        self.dataGrid.AppendRows()
        col = 0
        row = self.dataGrid.GetNumberRows() - 1
        for value in dataRecord:
            self.dataGrid.SetCellValue(row, col, value)
            col = col + 1
            if value == "running":
                self.dataGrid.SetCellBackgroundColour(row, col, (0, 255, 0))
            elif value == "stopped":
                self.dataGrid.SetCellBackgroundColour(row, col, (255, 0, 0))
            elif value == "pending":
                self.dataGrid.SetCellBackgroundColour(row, col, (255, 234, 0))
            elif value == "stopping":
                self.dataGrid.SetCellBackgroundColour(row, col, (255, 234, 0))
        self.resourcesDict[dataRecord[0]] = row
        self.dataGrid.AutoSize()

    def DeleteRows(self, pos=0, numRows=1, updateLabels=True):
        return self.dataGrid.DeleteRows(pos, numRows, updateLabels)

    def UpdateRow(self, dataRecord):
        row = self.resourcesDict.get(dataRecord[0], -1)
        if row == -1:
            debug_print("New item {0}.".format(dataRecord[0]))
            self.AppendRow(dataRecord)
        else:
            col = 0
            for value in dataRecord:
                debug_print("Updating {0} at row {1}".format(dataRecord[0], row))
                self.dataGrid.SetCellValue(row, col, value)
                if value == "running":
                    self.dataGrid.SetCellBackgroundColour(row, col, (0, 255, 0))
                elif value == "stopped":
                    self.dataGrid.SetCellBackgroundColour(row, col, (255, 0, 0))
                elif value == "pending":
                    self.dataGrid.SetCellBackgroundColour(row, col, (255, 234, 0))
                elif value == "stopping":
                    self.dataGrid.SetCellBackgroundColour(row, col, (255, 234, 0))
                col = col + 1
        self.dataGrid.AutoSize()

    def GetNumberRows(self):
        return self.dataGrid.GetNumberRows()


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
            self.resource = boto3.resource('ec2', region_name=regionName)
            try:
                instances = self.client.describe_instances()
                for instanceData in instances['Reservations']:
                    instanceId = instanceData['Instances'][0]['InstanceId']
                    instance = self.resource.Instance(instanceId)
                    record = []
                    record.append(instanceData['Instances'][0]['InstanceId'])
                    record.append(instanceData['Instances'][0]['InstanceType'])
                    record.append(instanceData['Instances'][0]['Placement']['AvailabilityZone'])
                    record.append(instanceData['Instances'][0]['PrivateIpAddress'])
                    if instanceData['Instances'][0]['State']['Name'] == "running":
                        record.append(instanceData['Instances'][0]['PublicIpAddress'])
                    else:
                        record.append("None")
                    for tag in instanceData['Instances'][0]['Tags']:
                        if tag['Key'] == "Name":
                            record.append(tag['Value'])
                    record.append(instanceData['Instances'][0]['State']['Name'])
                    wx.CallAfter(self.control.UpdateRow, record)
            except:
                print("Error getting data from region {0}.".format(regionName))
