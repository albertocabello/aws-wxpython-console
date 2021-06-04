#!/usr/bin/env python3

import wx
import wx.grid
import Actions
import Resources
import Extra

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="wxPython AWS manager", size=(1200, 600))
        self.Centre()

        # Create a panel and notebook (tabs holder)
        p = wx.Panel(self)
        nb = wx.Notebook(p)
        
        # Create the tab windows, add the windows to tabs and name them.
        ec2Labels = ['Id', 'Type', 'AZ', 'Private IP', 'Public IP', 'Name', 'State']
        self.tabEC2 = Resources.ThreadedPanel(nb, ec2Labels)
        self.tabEC2.Bind(wx.grid.EVT_GRID_CMD_CELL_LEFT_DCLICK, Actions.EC2Actions)
        nb.AddPage(self.tabEC2, "EC2 Instances")
        self.getInstances = Resources.GetInstancesThread(self.tabEC2)
        
        tabS3 = Resources.DataPanel(nb, dataFunction=Resources.GetBuckets)
        nb.AddPage(tabS3, "S3")
        
        tabUsers = Resources.DataPanel(nb, dataFunction=Resources.GetUsers)
        nb.AddPage(tabUsers, "Users")
        
        tabSG = Resources.DataPanel(nb, dataFunction=Resources.GetSecurityGroups)
        nb.AddPage(tabSG, "Security Groups")

        self.tabHTTPServers = Extra.HTTPServers(nb)
        nb.AddPage(self.tabHTTPServers, "HTTP/HTTPS")
        self.getHTTPServers = Extra.GetHTTPThread(self.tabHTTPServers)

        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, -1, wx.EXPAND)
        p.SetSizer(sizer)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.RefreshData, self.timer)
        self.timer.Start(5000)
        
    def Show(self):
        wx.Frame.Show(self)
        self.getInstances.start()
        self.getHTTPServers.start()

    def RefreshData(self, event):
        Resources.GetInstancesThread(self.tabEC2).start()
        Extra.GetHTTPThread(self.tabHTTPServers).start()

if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()
