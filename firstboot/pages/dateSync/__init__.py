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
import shlex
import subprocess
from gi.repository import Gtk
from firstboot_lib import PageWindow
from firstboot import serverconf

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

import firstboot.pages


__REQUIRED__ = False

__TITLE__ = _('Date Synchronization')


def get_page(main_window):

    page = DateSyncPage(main_window)
    return page


class DateSyncPage(PageWindow.PageWindow):
    __gtype_name__ = "DateSyncPage"

    def finish_initializing(self):
        self.set_status(None)

    def load_page(self, params=None):
        self.emit('status-changed', 'dateSync', not __REQUIRED__)

        self.ui.chkAutoconf.set_active(False)
        self.ui.txtAutoconf.set_sensitive(False)

        if serverconf.json_is_cached():
            self.ui.boxCheckAutoconf.set_visible(False)
            self.serverconf = serverconf.get_server_conf(None)
            self.ui.txtHost.set_text(self.serverconf.get_ntp_conf().get_host())

    def translate(self):
        desc = _('It is important that this workstation and the GECOS server have \
their time synchronized. From this page you can set the workstation time with an NTP server.')

        self.ui.lblDescription.set_text(desc)
        self.ui.chkAutoconf.set_label(_('Check this button if you want to get the \
default configuration from the server.'))
        self.ui.lblAutoconf.set_label(_('URL'))
        self.ui.lblHost.set_label(_('Host'))
        self.ui.btnSync.set_label(_('Synchronize'))

    def on_chkAutoconf_toggled(self, widget):
        self.ui.txtAutoconf.set_sensitive(self.ui.chkAutoconf.get_active())

    def on_btnSync_clicked(self, widget):

        self.ui.btnSync.set_sensitive(False)

        if self.ui.chkAutoconf.get_active():
            url = self.ui.txtAutoconf.get_text()
            try:
                self.serverconf = serverconf.get_server_conf(url)
                self.ui.txtHost.set_text(self.serverconf.get_ntp_conf().get_host())

            except Exception as e:
                self.set_status(1, str(e))
                self.ui.btnSync.set_sensitive(True)
                return

        cmd = 'ntpdate -u %s' % (self.ui.txtHost.get_text(),)
        args = shlex.split(cmd)

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #exit_code = os.waitpid(process.pid, 0)
        exit_code = process.wait()
        output = process.communicate()
        output = "%s%s" % (output[0].strip(), output[1].strip())

        self.ui.btnSync.set_sensitive(True)
        self.set_status(exit_code, output)

    def set_status(self, code, description=''):

        self.ui.imgStatus.set_visible(code != None)
        self.ui.lblStatus.set_visible(code != None)

        if code == None:
            return

        if code == 0:
            icon = Gtk.STOCK_YES

        else:
            icon = Gtk.STOCK_DIALOG_ERROR

        self.ui.imgStatus.set_from_stock(icon, Gtk.IconSize.MENU)
        self.ui.lblStatus.set_label(description)

    def previous_page(self, load_page_callback):
        load_page_callback(firstboot.pages.network)

    def next_page(self, load_page_callback):
        load_page_callback(firstboot.pages.pcLabel)
