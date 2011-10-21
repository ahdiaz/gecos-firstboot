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


from gi.repository import GObject, Gtk

import logging
logger = logging.getLogger('firstboot_lib')

import FirstbootEntry
from . helpers import get_builder, show_uri, get_help_uri

# This class is meant to be subclassed by FirstbootWindow.  It provides
# common functions and some boilerplate.
class PageWindow(Gtk.Window):
    __gtype_name__ = 'PageWindow'
    __page_container__ = 'ContainerWindow'

    __gsignals__ = {
        'page-changed': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)
        ),
        'status-changed': (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_STRING, GObject.TYPE_BOOLEAN)
        )
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

    def __init__(self, main_window=None):
        GObject.GObject.__init__(self)

    def __new__(cls, main_window):
        """Special static method that's automatically called by Python when
        constructing a new instance of this class.

        Returns a fully instantiated BaseFirstbootWindow object.
        """
        builder = get_builder(cls.__gtype_name__)
        new_object = builder.get_object(cls.__page_container__)
        new_object._finish_initializing(builder, main_window)

        return new_object

    def _finish_initializing(self, builder, main_window):
        """Called while initializing this instance in __new__

        finish_initializing should be called after parsing the UI definition
        and creating a FirstbootWindow object with it in order to finish
        initializing the start of the new FirstbootWindow instance.
        """

        self.main_window = main_window
        self.cmd_options = main_window.cmd_options
        self.fbe = FirstbootEntry.FirstbootEntry()
        self.builder = builder
        self.ui = builder.get_ui(self, True)

        self.page = builder.get_object(self.__gtype_name__)
        container = builder.get_object(self.__page_container__)
        container.remove(self.page)

        # Call the page specific initialization stuff
        self.finish_initializing()
        self.translate()

    def on_destroy(self, widget, data=None):
        """Called when the FirstbootWindow is closed."""
        # Clean up code for saving application state should be added here.
        Gtk.main_quit()

    def finish_initializing(self):
        pass

    def translate(self):
        pass

    def get_widget(self):
        return self.page

    def load_page(self, params=None):
        pass

    def unload_page(self, params=None):
        pass

    def previous_page(self, load_page_callback):
        pass

    def next_page(self, load_page_callback):
        pass
