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
            status = "unknown"

            try:
                connection = http.client.HTTPSConnection(HTTPServerName, HTTPServerPort, timeout=2)
                connection.request("GET", "/", headers={"Host": HTTPServerName})
                response = connection.getresponse()
                Resources.debug_print("HTTPS {0} gives {1}.".format(HTTPServer, response.status))
                if response.status != None:
                    status = "running"
            except ConnectionRefusedError:
                record = [HTTPServerName, HTTPServerPort, "stopped"]
            except Exception as ex:
                Resources.debug_print("HTTPS {0} gives error {1}.".format(HTTPServer, str(ex)))
            
            try:
                connection = http.client.HTTPConnection(HTTPServerName, HTTPServerPort, timeout=2)
                connection.request("GET", "/", headers={"Host": HTTPServerName})
                response = connection.getresponse()
                Resources.debug_print("HTTP {0} gives {1}.".format(HTTPServer, response.status))
                if response.status != None:
                    status = "running"
            except ConnectionRefusedError:
                status = "stopped"
            except Exception as ex:
                Resources.debug_print("HTTP {0} gives error {1}.".format(HTTPServer, str(ex)))

            record = [HTTPServerName, HTTPServerPort, status]
            wx.CallAfter(self.control.UpdateRow, record)
