#!/usr/bin/env python3

import wx
import wx.grid
import Resources

# Define the tab content as classes:

class TabFour(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is the last tab", (20,20))


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="wxPython AWS manager", size=(1200, 600))
        self.Centre()

        # Create a panel and notebook (tabs holder)
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        # Create the tab windows, add the windows to tabs and name them.
        tabEC2 = Resources.ThreadedPanel(nb, colLabels=['Id', 'Type', 'AZ', 'Private IP', 'Name', 'State'])
        nb.AddPage(tabEC2, "EC2")
        self.getInstances = Resources.GetInstancesThread(tabEC2)
        tabS3 = Resources.DataPanel(nb, dataFunction=Resources.GetBuckets)
        nb.AddPage(tabS3, "S3")
        tabUsers = Resources.DataPanel(nb, dataFunction=Resources.GetUsers)
        nb.AddPage(tabUsers, "Users")
        tab4 = TabFour(nb)
        nb.AddPage(tab4, "Tab 4")

        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
        
    def Show(self):
        wx.Frame.Show(self)
        self.getInstances.start()


if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()
