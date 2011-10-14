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
from firstboot_lib import PageWindow

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

import firstboot.pages


__REQUIRED__ = False

__TITLE__ = _('Describe this workstation')

__LABEL_FILE__ = '/etc/pclabel'


def get_page(options=None):

    page = PCLabelPage(options)
    return page

class PCLabelPage(PageWindow.PageWindow):
    __gtype_name__ = "PCLabelPage"

    def finish_initializing(self, builder, options=None):
        self.lblDescription = builder.get_object('lblDescription')
        self.imgStatus = builder.get_object('imgStatus')
        self.lblStatus = builder.get_object('lblStatus')
        self.lblLabel = builder.get_object('lblLabel')
        self.txtLabel = builder.get_object('txtLabel')

        self.txtLabel.set_text(self.get_label())
        self.imgStatus.set_visible(False)
        self.lblStatus.set_visible(False)

    def translate(self):
        desc = _('You can type a description for this workstation, it will be \
shown in the GECOS Server admin interface and will help you to find out the \
workstation later.')

        self.lblDescription.set_text(desc)
        self.lblLabel.set_label(_('Label'))

    def on_txtLabel_changed(self, entry):
        try:
            self.set_label(self.txtLabel.get_text())
            self.imgStatus.set_from_stock(Gtk.STOCK_YES, Gtk.IconSize.MENU)
            self.lblStatus.set_label(_('The label has been updated correctly.'))

        except Exception as e:
            self.imgStatus.set_from_stock(Gtk.STOCK_DIALOG_ERROR, Gtk.IconSize.MENU)
            self.lblStatus.set_label(str(e))

        self.imgStatus.set_visible(True)
        self.lblStatus.set_visible(True)

    def get_label(self):

        label = ''

        if os.path.exists(__LABEL_FILE__):
            fd = open(__LABEL_FILE__, 'r')
            if fd != None:
                label = fd.read()
                fd.close()

        return label

    def set_label(self, label):
        fd = open(__LABEL_FILE__, 'w')
        if fd != None:
            fd.write(label)
            fd.close()

    def previous_page(self, load_page_callback):
        load_page_callback(firstboot.pages.network)

    def next_page(self, load_page_callback):
        load_page_callback(firstboot.pages.linkToServer)
