#!/usr/bin/env python3

import http.client
import threading
import wx

import Resources

class HTTPServers(Resources.ThreadedPanel):

    def __init__(self, parent=None):
        Resources.ThreadedPanel.__init__(self, parent, ['Servidor', 'Puerto', 'Status'])


class GetHTTPThread(threading.Thread):

    def __init__(self, control):
        threading.Thread.__init__(self)
        self.servers = ["www.debian.org:443", "www.juntaex.es:80", "github.com:443"]
        self.control = control

    def run(self):
        for HTTPServer in self.servers:
            HTTPServerName, HTTPServerPort = HTTPServer.split(":")
            Resources.debug_print("Checking server {0}.".format(HTTPServerName))
            connection = http.client.HTTPSConnection(HTTPServerName, HTTPServerPort, timeout=2)
            try:
                connection.request("GET", "/")
                response = connection.getresponse()
                status = "unknown"
                Resources.debug_print("{0} gives {1}.".format(HTTPServer, response.status))
                if response.status == 400:
                    connection = http.client.HTTPConnection(HTTPServerName, HTTPServerPort, timeout=2)
                    connection.request("GET", "/")
                    response = connection.getresponse()
                if response.status == 200:
                    status = "running"
                record = [HTTPServerName, HTTPServerPort, status]
                wx.CallAfter(self.control.UpdateRow, record)
            except ConnectionRefusedError:
                record = [HTTPServerName, HTTPServerPort, "stopped"]
                wx.CallAfter(self.control.UpdateRow, record)
            except:
                print("Error getting data from {0}.".format(HTTPServer))
                record = [HTTPServerName, HTTPServerPort, "unknown"]
                wx.CallAfter(self.control.UpdateRow, record)
