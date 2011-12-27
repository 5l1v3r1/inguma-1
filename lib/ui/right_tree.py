##      right_tree.py
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

import os
import gtk

import lib.ui.core as core
import lib.ui.config as config

class KBtree(gtk.TreeView):

    def __init__(self, node_menu):
        # TreeStore
        self.treestore = gtk.TreeStore(gtk.gdk.Pixbuf, str, str)
        # create the TreeView using treestore
        super(KBtree,self).__init__(self.treestore)

        self.uicore = core.UIcore()
        self.node_menu = node_menu

        self.xdot = None
        # nodes will store graph nodes used for automove on kbtree click
        self.nodes = {}

        # Tree icons
        self.default_icon = gtk.gdk.pixbuf_new_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'icons' + os.sep + 'generic.png')
        self.node_icon = gtk.gdk.pixbuf_new_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'node.png')
        self.value_icon = gtk.gdk.pixbuf_new_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'value.png')

        # Main VBox to store right panel elements
        self.right_vbox = gtk.VBox(False)

        # OS visibility
        self.os_visible = {}
        self.os_visible['generic'] = True
        for oss in config.ICONS:
            self.os_visible[oss.lower()] = True

        # OS buttons bar
        self.oss_bar = gtk.Toolbar()
        self.oss_bar.set_show_arrow(True)
        self.oss_bar.set_style(gtk.TOOLBAR_ICONS)
        self.create_os_buttons()

        #################################################################
        # Scrolled Window and Co
        #################################################################

        # Target filter text entry
        # expand/collapse buttons
        self.tgt_hbox = gtk.HBox(False)

        self.expand_btn = gtk.Button()
        self.expand_icon = gtk.Image()
        self.expand_icon.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU)
        self.expand_btn.set_image(self.expand_icon)
        self.expand_btn.set_relief(gtk.RELIEF_NONE)
        self.expand_btn.set_tooltip_text('Expand all nodes')
        self.expand_btn.connect('clicked', self._expand_all)

        self.collapse_btn = gtk.Button()
        self.collapse_icon = gtk.Image()
        self.collapse_icon.set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU)
        self.collapse_btn.set_image(self.collapse_icon)
        self.collapse_btn.set_relief(gtk.RELIEF_NONE)
        self.collapse_btn.set_tooltip_text('Collapse all nodes')
        self.collapse_btn.connect('clicked', self._collapse_all)

        sep = gtk.VSeparator()

        self.tgt_entry = gtk.Entry(20)
        self.tgt_entry.set_icon_from_stock(1, gtk.STOCK_CLEAR)
        self.tgt_entry.set_icon_tooltip_text(1, 'Clear entry')
        self.tgt_entry.connect('icon-press', self._clear_entry)
        self.tgt_entry.connect('changed', self._do_filter)

        self.tgt_hbox.pack_start(self.expand_btn, False, False, 0)
        self.tgt_hbox.pack_start(self.collapse_btn, False, False, 0)
        self.tgt_hbox.pack_start(sep, False, False, 2)
        self.tgt_hbox.pack_start(self.tgt_entry, True, True, 0)

        self.right_vbox.pack_start(self.tgt_hbox, False, False, 1)

        # Scrolledwindow/Treeview
        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolled_window.set_size_request(250,-1)

        self.modelfilter = self.treestore.filter_new()

        self.modelfilter.set_visible_func(self.visible_cb)
        self.set_model(self.modelfilter)

        self.set_rules_hint(True)
        self.set_enable_tree_lines(True)

        # Fill by default with targets info
        self.create_targets_tree()
        self.update_targets_tree()
        self.expand_all()

        # Add Textview to Scrolled Window
        self.scrolled_window.add_with_viewport(self)

        self.right_vbox.pack_start(self.scrolled_window, True, True, 0)

    def create_os_buttons(self):
        # OS filter buttons

        self.remove_os_buttons()

        counter = 0
        added_os = []
        kb = self.uicore.get_kbList()
        targets = kb['targets']
        for target in targets:
            if kb.has_key(target + '_os'):
                oss = kb[target + '_os'][0].lower()
                for os_icon in config.ICONS:
                    if os_icon in oss and os_icon not in added_os:
                        btn = self.create_os_button(os_icon)
                        self.oss_bar.insert(btn, counter)
                        counter += 1
                        added_os.append(os_icon)
            else:
                if 'generic' not in added_os:
                    btn = self.create_os_button('generic', True)
                    self.oss_bar.insert(btn, counter)
                    counter += 1
                    added_os.append('generic')

        if len(self.oss_bar.get_children()) > 1:
            self.right_vbox.pack_start(self.oss_bar, False, False, 1)
            self.oss_bar.show_all()

    def create_os_button(self, oss, generic=False):
        if not generic:
            btn = gtk.ToggleToolButton(oss)
            btn.set_label(oss.capitalize())
            btn.set_tooltip_text(oss.capitalize())
            icon = gtk.Image()
            icon.set_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'icons' + os.sep + oss + '.png')
            btn.set_icon_widget(icon)
            btn.set_active(True)
            self.os_visible[oss.lower()] = True
            btn.connect('toggled', self._filter_on_toggle)
        else:
            btn = gtk.ToggleToolButton()
            btn.set_label('Generic')
            btn.set_tooltip_text('Generic')
            self.os_visible['generic'] = True
            icon = gtk.Image()
            icon.set_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'icons' + os.sep + 'generic.png')
            btn.set_icon_widget(icon)
            btn.set_active(True)
            btn.connect('toggled', self._filter_on_toggle)

        return btn

    def create_model(self, mode):
        # Clear before changing contents
        self.treestore.clear()
        self.remove_columns()

        if mode == 'Targets':
            self.create_targets_tree()
            self.update_targets_tree()
        elif mode == 'Vulnerabilities':
            self.create_targets_tree()
            self.create_vulns_tree()

        # Update all
        self.expand_all()

    def remove_columns(self):
        columns = self.get_columns() 
        for column in columns:
            self.remove_column(column)

    def remove_os_buttons(self):
        for child in self.oss_bar.get_children():
            self.oss_bar.remove(child)
        if self.oss_bar in self.right_vbox:
            self.right_vbox.remove(self.oss_bar)

    def create_vulns_tree(self):
        ids = {}
        kb = self.uicore.get_kbList()
        # Add all hosts
        targets = kb['targets']
        targets.sort()
        for host in targets:
            if host + '_80-web-vulns' in kb.keys():
                if host + '_os' in kb:
                    target_os = kb[host + '_os'][0]
                    for oss in config.ICONS:
                        if oss.capitalize() in target_os:
                            icon = gtk.gdk.pixbuf_new_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'icons' + os.sep + oss + '.png')
                            piter = self.treestore.append(None, [icon, host, oss])
                else:
                    piter = self.treestore.append(None, [self.default_icon, host, 'generic'])
                for id, vuln in kb[host + '_80-web-vulns']:
                    if id not in ids.keys():
                        #print "Set element:", element
                        iditer = self.treestore.append( piter, [self.node_icon, id, None])
                        self.treestore.append( iditer, [self.value_icon, vuln, None])
                        ids[id] = iditer
                    else:
                        self.treestore.append( ids[id], [self.value_icon, vuln, None])

    def create_targets_tree(self):

        # create the TreeViewColumn to display the data
        self.tvcolumn = gtk.TreeViewColumn('Hosts')

        # add tvcolumn to treeview
        self.append_column(self.tvcolumn)

        # create a CellRendererText to render the data
        self.cell = gtk.CellRendererText()
        self.rendererPix = gtk.CellRendererPixbuf()

        # add the cell to the tvcolumn and allow it to expand
        self.tvcolumn.pack_start(self.rendererPix, False)
        self.tvcolumn.pack_start(self.cell, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        self.tvcolumn.set_attributes(self.rendererPix, pixbuf=0)
        self.tvcolumn.set_attributes(self.cell, text=1)
        #self.tvcolumn.add_attribute(self.cell, 'text', 1)

        # make it searchable
        self.set_search_column(1)

        # Allow sorting on the column
        self.tvcolumn.set_sort_column_id(1)

        # Allow drag and drop reordering of rows
        self.set_reorderable(True)

        # Connect right click popup search menu
        self.popup_handler = self.connect('button-press-event', self.popup_menu)

    def update_targets_tree(self):
        '''Reads KB and updates TreeView'''

        self.treestore.clear()

        kb = self.uicore.get_kbList()
        # Add all hosts
        targets = kb['targets']
        targets.sort()
        for host in targets:
            if host + '_os' in kb:
                target_os = kb[host + '_os'][0]
                for oss in config.ICONS:
                    if oss.capitalize() in target_os:
                        icon = gtk.gdk.pixbuf_new_from_file('lib' + os.sep + 'ui' + os.sep + 'data' + os.sep + 'icons' + os.sep + oss + '.png')
                        piter = self.treestore.append(None, [icon, host, oss])
            else:
                piter = self.treestore.append(None, [self.default_icon, host, 'generic'])
            for element in kb:
                if element.__contains__(host + '_'):
#                    self.treestore.append( piter, [element.split('_')[-1].capitalize()])
                    #print "Set element:", element
                    eiter = self.treestore.append( piter, [self.node_icon, element.split('_')[-1].capitalize(), None])

                    for subelement in kb[element]:
                        if subelement is list:
                            #print "\tSet subelement list:", subelement
                            for x in subelement:
                                self.treestore.append( eiter, [self.value_icon, x, None] )
                        else:
                            #print "\tSet subelement not list:", subelement
                            self.treestore.append( eiter, [self.value_icon, subelement, None] )

            if self.xdot:
                #function = ''
                for node in self.xdot.graph.nodes:
                    if node.url:
                        target = node.url
                        self.nodes[target] = [node.x, node.y]
        # Update OS bar
        self.create_os_buttons()

    def _expand_all(self, widget):
        self.expand_all()

    def _collapse_all(self, widget):
        self.collapse_all()

    def _clear_entry(self, entry, icon_pos, event):
        entry.set_text('')
        self.modelfilter.refilter()

    def _do_filter(self, widget):
        '''filter treeview while user types'''
        self.modelfilter.refilter()

    def _filter_on_toggle(self, widget):
        os_name = widget.get_label().lower()
        self.os_visible[os_name] = widget.get_active()
        self.modelfilter.refilter()

    def visible_cb(self, model, iter):
        data = self.tgt_entry.get_text()
        # Just filter root nodes, so we check iter path
        if len(model.get_path(iter)) == 1:
            # Check os filter buttons
            if model.get_value(iter, 2) and self.os_visible:
                if not self.os_visible[model.get_value(iter, 2)]:
                    return False
                else:
                    # Just filter if text entry is filled
                    if data:
                        return data in model.get_value(iter, 1)
                    else:
                        return True
            else:
                return True
        else:
            return True

    def popup_menu(self, tree, event):
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            #(path, column) = tree.get_cursor()
            (path, column, x, y) = tree.get_path_at_pos(int(event.x), int(event.y))
            # Is it over a plugin name ?
            # Ge the information about the click
            if path is not None and len(path) == 1 and self.nodes:
                node = self.treestore[path][1]
                if node in self.nodes:
                    self.xdot.animate_to( int(self.nodes[node][0]), int(self.nodes[node][1]) )
        elif event.button == 3:
            #(path, column) = tree.get_cursor()
            (path, column, x, y) = tree.get_path_at_pos(int(event.x), int(event.y))
            # Is it over a plugin name ?
            # Ge the information about the click
            if path is not None and len(path) == 1:
                node = self.treestore[path][1]
                self.node_menu.set_data(node)
                self.node_menu.popmenu.popup(None, None, None, 1, event.time)
