##      nmapscan.py
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

import sys, os
sys.path.append('../..')
import lib.IPy as IPy

#from . import core
from . import config

class NmapScan:
    '''Dialog for add targets to the KB'''

    #def __init__(self, module, core):
    def __init__(self, ip):

        TITLE = "Nmap Scan Module"
        nmap = getattr(config, 'NMAP_PATH')
        self.profiles = getattr(config, 'NMAP_PROFILES')
        self.ip = ip

#        # Core instance for manage the KB
#        self.uicore = core
#        # Module to be launched after insert the data
#        self.module = module

        # Dialog
        self.dialog = gtk.Dialog(title=TITLE, parent=None, buttons=(gtk.STOCK_HELP, gtk.RESPONSE_HELP, gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK))
        self.dialog.resize(250, 75)

        # Label 
        self.tglab = gtk.Label('Target:')
        self.tglab.set_alignment(0.0, 0.5)

        # A target text entry
        self.tgentry = gtk.Entry(max=15)
        self.tgentry.set_text(self.ip)

        # Label 
        self.prolab = gtk.Label('Profile:')
        self.prolab.set_alignment(0.0, 0.5)

        # A ComboBox
        self.combobox = gtk.combo_box_new_text()
        for profile in self.profiles.keys():
            self.combobox.append_text(profile)
        self.combobox.connect('changed', self.changed_cb)

        # Label 
        self.comlab = gtk.Label('Command:')
        self.comlab.set_alignment(0.0, 0.5)

        # A target text entry
        self.comentry = gtk.Entry(max=125)
        self.comentry.set_text('nmap -v -A ' + self.ip)

        # Separator
        self.sep = gtk.HSeparator()

        # ProgressBar
        self.progressbar = gtk.ProgressBar(adjustment=None)

        #########################################################
        # Table
        table = gtk.Table(rows=5, columns=4, homogeneous=False)
        table.set_row_spacings(2)
        table.set_col_spacings(2)

        # Add lements to Table
        table.attach(self.tglab, 0, 1, 0, 1)
        table.attach(self.tgentry, 1, 2, 0, 1)
        table.attach(self.prolab, 2, 3, 0, 1)
        table.attach(self.combobox, 3, 4, 0, 1)
        table.attach(self.comlab, 0, 1, 1, 2)
        table.attach(self.comentry, 1, 4, 1, 2)
        table.attach(self.sep, 1, 3, 2, 3)
        table.attach(self.progressbar, 0, 5, 3, 4)

        # Add HBox to VBox
        self.dialog.vbox.pack_start(table, False, False, 2)

        #########################################################
        # the help button
        self.butt_help = self.dialog.action_area.get_children()[2]
        self.butt_help.connect("clicked", lambda x: self.show_help())
        # the cancel button
        self.butt_cancel = self.dialog.action_area.get_children()[1]
        self.butt_cancel.connect("clicked", lambda x: self.dialog.destroy())

        # the save button
        self.butt_save = self.dialog.action_area.get_children()[0]
        #self.butt_save.set_sensitive(False)
        #self.butt_save.connect("clicked", self.insertData, data)
        self.butt_save.connect("clicked", self.validateData)

        # Finish
        self.dialog.show_all()
        self.dialog.show()

    def validateData(self, widget):
        '''Validate user input and call insertData when done'''

        try:
            if self.tgentry.get_text():
                ip = IPy.IP( self.tgentry.get_text() )
            #self.dialog.destroy()
            self.run_nmap()
        except:
            self.show_error_dlg( self.tgentry.get_text() + ' is not a valid IP address')

    def run_nmap(self):

        # Start progressbar
        self.progressbar.pulse()
        self.progressbar.set_pulse_step(0.80)
        self.progressbar.set_text('Running Nmap, please wait')

        # Create and read popen
        command = self.comentry.get_text()
        command += ' -oX /tmp/nmapxml.xml'
        self.uicore.run_system_command(command)
        self.progressbar.set_text('Parsing Data...')
        #Destroy dialog
        self.parse_data()
        self.dialog.destroy()

    def parse_data(self):

            import lib.ui.nmapParser as nmapParser
            try:
                self.gom.echo( 'Parsing scan results...', False)
                nmapData = nmapParser.parseNmap('/tmp/nmapxml.xml')
                self.gom.echo( 'Inserting data in KB...', False)
                nmapParser.insertData(self.uicore, nmapData)


                askASN = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format="Resolve ASN of IP addresses?")
                do_asn = askASN.run()

                self.gom.echo( 'Loaded\nUpdating Graph', False)

                if do_asn == gtk.RESPONSE_YES:
                    self.uicore.getDot(doASN=True)
                else:
                    self.uicore.getDot(doASN=False)
                askASN.destroy()

                self.gom.update_graph( self.uicore.get_kbfield('dotcode') )
                self.gom.kbwin.updateTree()

            except:
                md = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format="Error loading file")
                md.run()
                md.destroy()


    def show_help(self):
        help = os.popen('nmap --help')
        help_text = help.read()
        help.close()
        helpdlg = HelpDialog(help_text)
        enditer = helpdlg.output_buffer.get_end_iter()
        helpdlg.output_buffer.insert(enditer, help_text + '\n')

    def changed_cb(self, entry):
        model = self.combobox.get_model()
        active = self.combobox.get_active()
        if active < 0:
            return None
        self.comentry.set_text( self.profiles[ model[active][0] ] + self.tgentry.get_text() )

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

class HelpDialog(gtk.Dialog):
    '''Window to popup help output'''

    def __init__(self, text_msg):
        super(HelpDialog,self).__init__('Nmap Help', None, gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK,gtk.RESPONSE_ACCEPT))

        # the cancel button
        self.butt_cancel = self.action_area.get_children()[0]
        self.butt_cancel.connect("clicked", lambda x: self.destroy())

        # Positions
        self.resize(550, 500)
        self.set_position(gtk.WIN_POS_CENTER)

        # Log TextView
        #################################################################
        self.output_text = gtk.TextView(buffer=None)
        self.output_text.set_wrap_mode(gtk.WRAP_NONE)
        self.output_text.set_editable(False)
        self.output_buffer = self.output_text.get_buffer()

        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.scrolled_window.is_visible = True

        #Always on bottom on change
        self.vajd = self.scrolled_window.get_vadjustment()
        self.scrolled_window.add_with_viewport(self.output_text)

        self.vbox.pack_start(self.scrolled_window)
        self.show_all()
