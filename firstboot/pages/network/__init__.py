# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# This file is part of Guadalinex
#
# This software is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this package; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

__author__ = "Antonio Hernández <ahernandez@emergya.com>"
__copyright__ = "Copyright (C) 2011, Junta de Andalucía <devmaster@guadalinex.org>"
__license__ = "GPL-2"


import os
from gi.repository import Gtk
from gi.repository import GObject
from firstboot_lib import PageWindow

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

from interface import localifs, internet_on

__REQUIRED__ = True

__TITLE__ = _('Configure the network')

def get_page(options=None):

    page = NetworkPage(options)
    return page

class NetworkPage(PageWindow.PageWindow):
    __gtype_name__ = "NetworkPage"

    __gsignals__ = {
        'link-status': (GObject.SignalFlags.ACTION, None, (GObject.TYPE_BOOLEAN,))
    }

    # To construct a new instance of this method, the following notable
    # methods are called in this order:
    # __new__(cls)
    # __init__(self)
    # finish_initializing(self, builder)
    # __init__(self)
    #
    # For this reason, it's recommended you leave __init__ empty and put
    # your initialization code in finish_initializing

    def finish_initializing(self, builder, options=None):
        """Called while initializing this instance in __new__

        finish_initializing should be called after parsing the UI definition
        and creating a FirstbootWindow object with it in order to finish
        initializing the start of the new FirstbootWindow instance.
        """
        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.ui = builder.get_ui(self, True)

        self.cmd_options = options

        container = builder.get_object(self.__page_container__)
        page = builder.get_object(self.__gtype_name__)
        container.remove(page)
        self.page = page

        self.treeviewInterfaces = builder.get_object('treeviewInterfaces')

        self.timer_ret = True

        self.translate()
        self.init_treeviewInterfaces()

    def translate(self):
        self.builder.get_object('btnNetworkDialog').set_label(_('Configure the network'))
        self.builder.get_object('lblDescription').set_text(_('You need to be connected to the network \
for linking this workstation to a GECOS server and for installing software.'))
        self.builder.get_object('lblDescription1').set_text(_('Below are shown the current \
detected interfaces.'))

    def load_page(self, assistant):
        self.timer_ret = True
        GObject.timeout_add_seconds(1, self.load_treeviewInterfaces)

    def unload_page(self):
        self.timer_ret = False

    def get_widget(self):
        return self.page

    def on_btnNetworkDialog_Clicked(self, button):
        cmd = 'nm-connection-editor'
        os.spawnlp(os.P_NOWAIT, cmd, cmd)

    def init_treeviewInterfaces(self):

        tvcolumn = Gtk.TreeViewColumn(_('Name'))
        cell = Gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.set_cell_data_func(cell, self._render_column_name)
        self.treeviewInterfaces.append_column(tvcolumn)

        tvcolumn = Gtk.TreeViewColumn(_('IP'))
        cell = Gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.set_cell_data_func(cell, self._render_column_ip)
        self.treeviewInterfaces.append_column(tvcolumn)

        selection = self.treeviewInterfaces.get_selection()
        selection.set_mode(Gtk.SelectionMode.NONE)

        self.load_treeviewInterfaces()

    def load_treeviewInterfaces(self):

        n_ifaces = 0

        store = self.treeviewInterfaces.get_model()
        store.clear()

        ifs = localifs()
        #print ifs

        for _if in ifs:
            store.append([_if[0], _if[1]])
            if _if[0] != 'lo' and len(_if[1]) > 0:
                n_ifaces += 1

        self.emit('link-status', n_ifaces > 0)
        self.treeviewInterfaces.set_model(store)

        return self.timer_ret

    def _render_column_name(self, column, cell, model, iter, user_param):

        value = model.get_value(iter, 0)
        text = '<b>%s</b>' % (value,)
        cell.set_property('markup', text)
        cell.set_property('width', 80)

    def _render_column_ip(self, column, cell, model, iter, user_param):

        value = model.get_value(iter, 1)
        cell.set_property('text', value)
