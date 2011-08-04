# -*- coding: utf-8 -*-
"""
Inguma Penetration Testing Toolkit
Copyright (C) 2011 David Martínez Moreno <ender@debian.org>
This software is not affiliated in any way with Facebook, my current employer.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

class CIngumaModule:
    """ This module contains the common methods (mostly stubs) and variables
    for creating an Inguma module. """

    target = ""
    ports = []
    sport = 1025
    closed = {}
    opened = {}
    mac = {}
    services = {}
    waitTime = 0
    randomizeWaitTime = False
    timeout = 1
    iface = "eth0"
    results = {}
    dict = None
    interactive = True
    """ The following are used ONLY for exploits (shellcode) """
    command = ""
    listenPort = 4444
    ostype = 1
    payload = "bindshell"

    def printSummary(self):
        """ Method called when run() has returned True.  It's used for showing
        a summary of the execution to the user. """
        pass

    def run(self):
        """ Method called when the module is invoked.
        If it returns False, execution is stopped there.
        If it returns True, then printSummary() is called after run().
        """
        pass

    def show_help(self):
        """ Method called when 'help <module> is executed from the command line. """
        pass

    def show_help(self):
        """ Method called when the module is interactive and 'help' is executed
        from the command line. """
        pass

    def addToDict(self, element, value):
        """ It's used to add data to the knowledge base to be used, i.e., by other modules """
        if value == None:
            return

        if self.dict is not None:
            if self.dict.has_key(element):
            
                for x in self.dict[element]:
                    if x == value:
                        return

                self.dict[element] += [value]
            else:
                self.dict[element] = [value]

    def getPasswordList(self):
        fname = self.dict["base_path"]
        if fname != "" :
            fname += os.sep + "data" + os.sep + "dict"
        else:
            fname = "data" + os.sep + "dict"

        f = file(fname, "r")
        return f.readlines()

