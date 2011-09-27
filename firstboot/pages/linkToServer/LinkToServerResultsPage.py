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
import gtk
import subprocess
import shlex
import urllib
import urllib2
import json
import gobject

import ServerConf
from ServerConf import ServerConfException, LinkToLDAPException, LinkToChefException
from firstboot_lib import PageWindow, FirstbootEntry

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')


__REQUIRED__ = False

__TITLE__ = _('Link workstation to a server')

__STATUS_TEST_PASSED__ = 0
__STATUS_CONFIG_CHANGED__ = 1
__STATUS_CONNECTING__ = 2
__STATUS_ERROR__ = 3


def get_page(options=None):

    page = LinkToServerResultsPage(options)
    return page

class LinkToServerResultsPage(PageWindow.PageWindow):
    __gtype_name__ = "LinkToServerResultsPage"

    __gsignals__ = {
        'page-changed': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        ),
        'subpage-changed': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
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

    def finish_initializing(self, builder, options=None):
        """Called while initializing this instance in __new__

        finish_initializing should be called after parsing the UI definition
        and creating a FirstbootWindow object with it in order to finish
        initializing the start of the new FirstbootWindow instance.
        """

        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.ui = builder.get_ui(self, True)

        self.lblDescription = builder.get_object('lblDescription')
        self.boxMessageContainer = builder.get_object('boxMessageContainer')
        self.imgStatus = builder.get_object('imgStatus')
        self.lblStatus = builder.get_object('lblStatus')
        self.btnBack = builder.get_object('btnBack')
        self.btnAccept = builder.get_object('btnAccept')

        container = builder.get_object('ContainerWindow')
        page = builder.get_object('LinkToServerResultsPage')
        container.remove(page)
        self.page = page

        self.translate()

        self.cmd_options = options
        self.fbe = FirstbootEntry.FirstbootEntry()

        self.result = False

    def is_associated(self):
        return os.path.exists(ServerConf.__LDAP_BAK_FILE__)

    def translate(self):
        desc = _('When a workstation is linked to a GECOS server it can be \
managed remotely and existing users in the server can login into \
the workstation.\n\n')

        if not self.is_associated():
            desc_detail = _('For linking this workstation, type the URL where the \
configuration resides and click on "Link".')
        else:
            desc_detail = _('This workstation is currently linked to a GECOS \
server. If you want to unlink it click on "Unlink".')

        self.lblDescription.set_text(desc + desc_detail)

    def get_widget(self):
        return self.page

    def set_params(self, params):

        if 'server_conf' in params:
            self.server_conf = params['server_conf']

        if 'result' in params:
            self.result = params['result']

        if 'errors' in params:
            for e in params['errors']:
                box = self.new_message(e, gtk.STOCK_DIALOG_ERROR)
                self.boxMessageContainer.pack_start(box, False, False)

        if 'messages' in params:
            for m in params['messages']:
                box = self.new_message(m, gtk.STOCK_YES)
                self.boxMessageContainer.pack_start(box, False, False)

        if self.result == True:
            self.btnBack.set_visible(False)
            self.btnAccept.set_label(_('Finalize'))

        else:
            self.btnBack.set_visible(True)
            self.btnBack.set_label(_('Back'))
            self.btnAccept.set_label(_('Finalize'))

    def new_message(self, message, icon):
        box = gtk.HBox()
        img = gtk.Image()
        img.set_from_stock(icon, gtk.ICON_SIZE_MENU)
        img.show()
        lbl = gtk.Label()
        lbl.set_text(message)
        lbl.show()
        box.pack_start(img, False, True)
        box.pack_start(lbl, False, True)
        box.set_spacing(10)
        box.show()
        return box

    def on_btnBack_Clicked(self, button):
        self.emit('subpage-changed', 'linkToServer',
                  'LinkToServerConfEditorPage', {'server_conf': self.server_conf})

    def on_btnAccept_Clicked(self, button):
        self.emit('page-changed', 'linkToServer', {})
