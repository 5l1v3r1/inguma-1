#!/usr/bin/python
"""
Module udp ping for Inguma
Copyright (c) 2009 Hugo Teso <hugo.teso@gmail.com>

License is GPL
"""
import os
import time
from lib.libexploit import CIngumaModule

try:
    import scapy.all as scapy
    bHasScapy = True
except:
    bHasScapy = False

name = "udping"
brief_description = "UDP Ping"
type = "discover"

class CUdpPing(CIngumaModule):

    target = ""
    port = 135
    waitTime = 0
    up = {}
    down = {}
    timeout = 2
    exploitType = 0
    results = {}
    iface = scapy.get_working_if()
    wizard = False
    dict = None

    def help(self):
        print "target = <target host or network>"
        print "timeout = <timeout>"
        print "waitTime = <wait time between packets>"
        print "port = <destination port to ping>"
        print "iface = <iface>"

    def run(self):
        if not bHasScapy:
            print "No scapy support :("
            return False
        self.results = {}
        self.up = {}
        self.down = {}

        mTargets = scapy.IP(dst=self.target)
        
        for target in mTargets:
            self.gom.echo( "Sending probe to\t" + str(target.dst) + "\tusing port\t" + str(self.port) )
            p = scapy.IP(dst=target.dst)/scapy.UDP(dport=self.port)

            ans, unans = scapy.sr(p, timeout=self.timeout, iface=self.iface, retry=0)

#            self.gom.echo( ans.summary( lambda(s,r) : r.sprintf("%IP.src% is alive") ) )

            if ans:
                self.up[len(self.up)+1] = ans[0][0].dst
                self.addToDict("alive", ans[0][0].dst)
                self.addToDict("hosts", ans[0][0].dst)
                #self.addToDict(ans[0][0].dst + "_trace", ans[0][0].dst)
#                else:
#                    self.down[len(self.up)+1] = ans[0][0].dst
#                    self.gom.echo( "Answer of type " + str(icmptypes[ans[0][0].type]) + " from " + str(ans[0][0].dst) )

        self.results = self.up
        return True
    
    def printSummary(self):
        if len(self.results) == 0:
            return

        i = 0
        self.gom.echo( "" )
        self.gom.echo( "Discovered hosts" )
        self.gom.echo( "----------------" )
        self.gom.echo( "" )

        for res in self.results:
            i += 1
            self.gom.echo( "Found host " + str(i) + "\t" + str(self.results[res]) )

        print

if __name__ == "__main__":
    import sys
    objHostUp = CHostUp()
    objHostUp.iface = "eth0"

    if len(sys.argv) == 1:
        objHostUp.target = "192.168.1.1"
    else:
        objHostUp.target = sys.argv[1]

    objHostUp.run()

    for host in objHostUp.up:
        self.gom.echo( "Host " + str(host) +" is up" )
