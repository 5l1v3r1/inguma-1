#!/usr/bin/python

##      CNmapScan.py
#       
#       Copyright 2010 Hugo Teso <hugo.teso@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import sys, os, string
from lib.nmapparser import NmapParser
from lib.libexploit import CIngumaModule

name = "nmapscan"
brief_description = "A module for port scanning using Nmap"
type = "gather"

class CNmapScan(CIngumaModule):
    target = ""
    interactive = True

    def help(self):
        print "A module for port scanning using Nmap"

    def showHelp(self):
        print 
        print "Inguma's Nmap Interface Help"
        print "------------------------------"
        print
        print "help                     Show this help"
        print "nmaphelp                 Show Nmap's help"
        print "nmap <options>           Execute Nmap with options specified"
        print "exit                     Exit from nmapscan interface"
        print 

    def HelpNmap(self):
        self.gom.echo( os.popen('nmap --help').read() )

    def runNmap(self,  options):
        os.popen(options + " -oX /tmp/nmapxml.xml")
        nmapxml = open('/tmp/nmapxml.xml')
        
        parser = NmapParser()
        parser.parse(nmapxml)
        nmapxml.close()
        os.remove('/tmp/nmapxml.xml')
        
        #self.gom.echo( "Options: ",  parser.options )
        self.gom.echo( "Finish time:", parser.runstats.finished.time )
        
        h_stats = parser.runstats.hosts
        self.gom.echo( "Hosts -> total %s, up: %s, down: %s" % (h_stats.total, h_stats.up, h_stats.down) )
        
        for host in parser.host:
            #self.gom.echo( "Host options:", host.options )
            
            if host.hostnames:
                self.gom.echo( "Hostname:", host.hostnames[0]['name'] )
            self.gom.echo( "Host Address;",  host.address[0]['addr'] )
            self.gom.echo( "Host ports info:" )
            for p in host.ports.ports:
                self.gom.echo( "%7s%9s%6s" % (p.portid, p.state, p.protocol) )
                self.addToDict(host.address[0]['addr'] + "_tcp_ports", p.portid)
            
            if 'script' in host.ports.ports[0].options:
                self.gom.echo( "" )
                self.gom.echo( host.ports.ports[0].script[0].output )
                self.gom.echo( "" )

    def runLoop(self):
        while 1:
            try:
                res = raw_input("NMAP> ")
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except:
                print "raw_input:", sys.exc_info()[1]
            
            words = res.split(" ")

            if len(words) == 1 and words[0] == "":
                continue
            elif words[0].lower() == "nmap" and len(words)>1:
                mystring = string.join(words, ' ')
                self.runNmap(mystring)
            elif words[0].lower() == "nmaphelp":
                self.HelpNmap()
            elif words[0].lower() == "help":
                self.showHelp()
            elif words[0].lower() in ["exit", "quit"]:
                break
            else:
                print "Unknow option or command '%s'" % res

    def run(self):

        self.runLoop()

        return True

    def printSummary(self):
        """ If the method run of the module returns True printSummary will called after """
        pass
