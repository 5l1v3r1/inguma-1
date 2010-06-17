##      addTargetDlg.py
#       
#       Copyright 2009 Hugo Teso <hugo.teso@gmail.com>
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

import pygtk
import gtk, gobject

import sys, time, threading
sys.path.append('../..')
import lib.IPy as IPy

#from . import core

class addTargetDialog:
    '''Dialog for adding targets and run some modules'''

    def __init__(self, core):

        TITLE = "Scpecify target"

        self.DISCOVERS = ['hostname',
                    'tcptrace',
                    'asn',
                    'netcraft']

        self.GATHERS = ['tcpscan']

        # Core instance for manage the KB
        self.uicore = core

        # Dialog
        self.dialog = gtk.Dialog(title=TITLE, parent=None, flags=gtk.DIALOG_MODAL, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK))
        self.dialog.resize(250, 75)

        # Radio buttons
        self.ip_rbutton= gtk.RadioButton(group=None, label='Single IP')
        self.ip_rbutton.connect("toggled", self.rbcallback, "IP")
        self.active = 'IP'
        self.ip_rbutton.set_active(True)
        self.dom_rbutton = gtk.RadioButton(self.ip_rbutton, label='Domain')
        self.dom_rbutton.connect("toggled", self.rbcallback, "DOM")

        # A target text entry
        self.tgentry = gtk.Entry(max=30)
        self.tgentry.set_focus = True

        #########################################################
        # Table
        table = gtk.Table(rows=2, columns=2, homogeneous=True)
        table.set_row_spacings(2)
        table.set_col_spacings(2)

        # Add lements to Table
        table.attach(self.ip_rbutton, 0, 1, 0, 1)
        table.attach(self.dom_rbutton, 1, 2, 0, 1)
        table.attach(self.tgentry, 0, 2, 1, 2)

        # Add HBox to VBox
        self.dialog.vbox.pack_start(table, False, False, 2)

        #########################################################
        # the cancel button
        self.butt_cancel = self.dialog.action_area.get_children()[1]
        self.butt_cancel.connect("clicked", lambda x: self.dialog.destroy())

        # the save button
        self.butt_save = self.dialog.action_area.get_children()[0]
        self.butt_save.connect("clicked", self.validateData)

        # Finish
        self.dialog.show_all()
        self.dialog.show()

    def validateData(self, widget):
        '''Validate user input and call insertData when done'''

        if self.active == 'IP':
            try:
                if self.tgentry.get_text():
                    ip = IPy.IP( self.tgentry.get_text() )
                self.dialog.destroy()
                self.insertData('ip', ip)
            except:
                self.show_error_dlg( self.tgentry.get_text() + ' is not a valid IP address')
        elif self.active == 'DOM':
                self.insertData('dom', self.tgentry.get_text())
                self.dialog.destroy()

    def rbcallback(self, widget, data=None):
        self.active = data

    def insertData(self, type, ip):
        if type == 'ip':
            #print "Adding IP target: " + ip.strNormal()
            self.uicore.set_kbfield( 'target', ip.strNormal() )
            self.uicore.set_kbfield( 'hosts', ip.strNormal() )
        elif type == 'dom':
            #print "Adding Domain target: " + ip
            self.uicore.set_kbfield( 'target', ip )

        # Run discover modules
        t = threading.Thread(target=self.runDiscovers, args=(type,))
        t.start()
        #self.runDiscovers(type)

    def runDiscovers(self, type):

        if type == 'dom':
            print "Running ipaddr"
            self.uicore.uiRunDiscover('ipaddr', join=True)
            ipaddr = self.uicore.get_kbfield('hosts')
            ipaddr = ipaddr[-1]
            print "\tDone, setting target to " + ipaddr
            self.uicore.set_kbfield('target', ipaddr)

        for module in self.DISCOVERS:
            print "Running discover: " + module
            self.uicore.uiRunDiscover(module, join=True)

        for module in self.GATHERS:
            print "Running gather: " + module
            self.uicore.uiRunDiscover(module, join=True)

    def get_active_text(self, combobox):
        model = combobox.get_model()
        active = combobox.get_active()
        if active < 0:
            return None
        return model[active][0]

    def show_error_dlg(self, error_string):
        """This Function is used to show an error dialog when
        an error occurs.
        error_string - The error string that will be displayed
        on the dialog.
        """
        error_dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR
                    , message_format=error_string
                    , buttons=gtk.BUTTONS_OK)
        error_dlg.run()
        error_dlg.destroy()
