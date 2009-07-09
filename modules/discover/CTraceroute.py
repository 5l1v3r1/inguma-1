#!/usr/bin/python
"""
Module trace for Inguma based in the Scapy's implementation
Copyright (c) 2007 Joxean Koret <joxeankoret@yahoo.es>

License is GPL
"""
import os
import sys
import random
import socket

from lib.libexploit import CIngumaModule

try:
    if os.name == "nt":
        from lib.winscapy import IP, TCP, sr, conf, getmacbyip, get_working_if, traceroute, TracerouteResult
    else:
        from lib.scapy import IP, TCP, sr, conf, getmacbyip, get_working_if, traceroute, TracerouteResult
    
    bHasScapy = True
except:
    bHasScapy = False

name = "tcptrace"
brief_description = "Trace a route to a host(s)"
type = "discover"

class CTraceroute(CIngumaModule):

    target = ""
    ports = [21, 22, 23, 80, 443, 135, 139, 445, 1521, 1526, 1531, 1541, 1551, 1561, 7777, 7999, 8000, 8001, 8002, 8888]
    sport = random.randint(1024, 65535)
    dport = 80
    hosts = {}
    timeout = 10
    iface = get_working_if()
    tcp = 1
    minttl = 1
    maxttl = 20
    exploitType = 0
    results = {}
    wizard = False
    packets = None
    dict = None

    def help(self):
        print "target = <target host or network>"
        print "timeout = <timeout>"
        print "minttl = <minimun ttl>"
        print "maxttl = <maximun ttl>"
        print "sport = <source port>"
        print "dport = <destination port>"
        print "iface = <interface to use>"

    def run(self):
        if not bHasScapy:
            #print "No scapy support :("
            self.gom.echo( "No scapy support :(" )
            return False

        self.hosts = {}
        #mwaaaaaaaaaaaaaaaaaaaaaaaaaa
        #self.dict["hosts"] = []

        if self.tcp == 1:
            a,b = sr(IP(dst=self.target, ttl=(self.minttl,self.maxttl))/TCP(sport=self.sport, dport=self.dport), 
            timeout=self.timeout, iface = self.iface, retry = 0)
        else:
            a,b = sr(IP(dst=self.target, ttl=(self.minttl,self.maxttl)), retry=0)

        a = TracerouteResult(a.res)
        a.make_graph()
        self.packets = a

        start = 0
        for x in a:
            i = 0
            for y in x:
                if start == 0:
                    start = 1
                    self.hosts[len(self.hosts)+1] = y.src
                    self.addToDict("hosts", y.src)

                    continue

                if i == 0:
                    i = 1
                    continue

                self.hosts[len(self.hosts)+1] = y.src
                self.addToDict("hosts", y.src)

        try:
            self.hosts[len(self.hosts)+1] = y.src
            self.addToDict("hosts", y.src)
        except:
            # Ugly hack
            pass

        self.results = self.hosts
        return True

    def printSummary(self):
        idx = 0
        prevHost = ""

        if self.wizard:
            res = raw_input("Show graph (y/n) [y]: ")
            
            if res == "" or res.lower() == "y":
                res = raw_input("Path to file (otherwise display using ImageMagick): ")
                res3d = raw_input("Graphic 3D (y/n)[n]?: ")

                if res == "":
                    if res3d == "y":
                        self.packets.trace3D()
                    else:
                        self.packets.graph()
                else:
                    if res3d == "y":
                        self.packets.trace3D(target="> " + str(res))
                    else:
                        self.packets.graph(target="> " + str(res))

                return True

        self.gom.echo( "" )
        self.gom.echo( "Trace to target(s)" )
        self.gom.echo( "------------------" )
        self.gom.echo( "" )

        self.trace = []
        for res in self.results:
            idx += 1
            
            if prevHost == "":
                prevHost = self.results[res]
            elif prevHost == self.results[res]:
                self.gom.echo( "Prev host: " + prevHost + " actual host: " + self.results[res] )
                continue
            else:
                prevHost = self.results[res]

            self.gom.echo( "host " + str(idx) + "\t" + str(self.results[res]) )
            self.trace.append(self.results[res])

        self.gom.echo( "" )
        for element in self.trace:
            self.addToDict(self.target + "_trace", element)


if __name__ == "__main__":

    objTraceroute = CTraceroute()
    objTraceroute.target = "www.google.com"
    objTraceroute.tcp = 1
    objTraceroute.run()

    i = 0

    self.gom.echo( "Trace to" + objTraceroute.target )

    for host in objTraceroute.hosts:
        i += 1
        self.gom.echo( "host " + str(i) + "\t" + str(objTraceroute.hosts[host]) )


