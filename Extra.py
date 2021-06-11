#!/usr/bin/env python3

import datetime
import dateutil.parser
import http.client
import threading
import pytz
import urllib.request
import wx

import Resources

class HTTPServers(Resources.ThreadedPanel):

    def __init__(self, parent=None):
        Resources.ThreadedPanel.__init__(self, parent, ['Server', 'Port', 'Status', 'Certificate Expiry Date'])


class GetHTTPThread(threading.Thread):

    def __init__(self, control):
        threading.Thread.__init__(self)
        self.servers = ["www.debian.org:443", "www.juntaex.es:80", "github.com:443"]
        self.control = control

    def run(self):
        for HTTPServer in self.servers:
            HTTPServerName, HTTPServerPort = HTTPServer.split(":")
            status = "unknown"
            expiryDate = ""

            try:
                connection = http.client.HTTPSConnection(HTTPServerName, HTTPServerPort, timeout=2)
                connection.request("GET", "/", headers={"Host": HTTPServerName})
                response = connection.getresponse()
                Resources.debug_print("HTTPS {0} gives {1}.".format(HTTPServer, response.status))
                if response.status != None:
                    status = "running"
                    expiryDate = checkX509ExpiryDate(HTTPServerName, HTTPServerPort)
            except ConnectionRefusedError:
                record = [HTTPServerName, HTTPServerPort, "stopped", expiryDate]
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

            record = [HTTPServerName, HTTPServerPort, status, expiryDate]
            wx.CallAfter(self.control.UpdateRow, record)

def checkX509ExpiryDate(ServerName, Port='443'):
    context = urllib.request.ssl.create_default_context()
    with urllib.request.socket.create_connection((ServerName, Port)) as sock:
        ssock = context.wrap_socket(sock, server_hostname=ServerName)
    notAfter = ssock.getpeercert()['notAfter']
    date = dateutil.parser.parse(notAfter)
    now = datetime.datetime.now()
    remaining = (date - pytz.timezone('Europe/Madrid').localize(now)).days
    return "{0} (expires in {1} days)".format(notAfter, remaining)
