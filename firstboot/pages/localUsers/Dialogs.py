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

from gi.repository import Gtk

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')


def new_user_dialog():
    dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK_CANCEL)

    dialog.set_title(_('New user'))
    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_default_response(Gtk.ResponseType.OK)
    dialog.set_icon_name('dialog-password')
    dialog.set_markup(_('Type the new user information:'))

    hboxname = Gtk.HBox()
    lblname = Gtk.Label(_('name'))
    lblname.set_visible(True)
    hboxname.pack_start(lblname, False, False, False)
    name = Gtk.Entry()
    name.set_activates_default(True)
    name.show()
    hboxname.pack_end(name, False, False, False)
    hboxname.show()

    hboxlogin = Gtk.HBox()
    lbluser = Gtk.Label(_('login'))
    lbluser.set_visible(True)
    hboxlogin.pack_start(lbluser, False, False, False)
    user = Gtk.Entry()
    user.set_activates_default(True)
    user.show()
    hboxlogin.pack_end(user, False, False, False)
    hboxlogin.show()

    hboxpwd = Gtk.HBox()
    lblpwd = Gtk.Label(_('password'))
    lblpwd.set_visible(True)
    hboxpwd.pack_start(lblpwd, False, False, False)
    pwd = Gtk.Entry()
    pwd.set_activates_default(True)
    pwd.set_visibility(False)
    pwd.show()
    hboxpwd.pack_end(pwd, False, False, False)
    hboxpwd.show()

    hboxconfirm = Gtk.HBox()
    lblconfirm = Gtk.Label(_('confirm'))
    lblconfirm.set_visible(True)
    hboxconfirm.pack_start(lblconfirm, False, False, False)
    confirm = Gtk.Entry()
    confirm.set_activates_default(True)
    confirm.set_visibility(False)
    confirm.show()
    hboxconfirm.pack_end(confirm, False, False, False)
    hboxconfirm.show()

    dialog.get_message_area().pack_start(hboxname, False, False, False)
    dialog.get_message_area().pack_start(hboxlogin, False, False, False)
    dialog.get_message_area().pack_start(hboxpwd, False, False, False)
    dialog.get_message_area().pack_start(hboxconfirm, False, False, False)
    result = dialog.run()

    retval = False
    if result == Gtk.ResponseType.OK:
        retval = {
            'name': name.get_text(),
            'login': user.get_text(),
            'password': pwd.get_text(),
            'confirm': confirm.get_text(),
            'groups': ''
        }

    dialog.destroy()
    return retval


def remove_user_dialog(user):
    dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK_CANCEL)
    dialog.set_title(_('Remove user'))
    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_default_response(Gtk.ResponseType.OK)
    dialog.set_icon_name('dialog-password')
    dialog.set_markup(_('The user %s is going to be removed, are you sure?' % (user['login'],)))

    hboxuser = Gtk.HBox()
    check = Gtk.CheckButton(_('Remove the user home?'))
    check.show()
    hboxuser.pack_start(check, False, False, False)
    hboxuser.show()

    dialog.get_message_area().pack_start(hboxuser, False, False, False)
    result = dialog.run()

    retval = False
    if result == Gtk.ResponseType.OK:
        retval = [True, check.get_active()]

    dialog.destroy()
    return retval


def user_error_dialog(message):
    dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK)
    dialog.set_title(_('Error'))
    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_default_response(Gtk.ResponseType.OK)
    dialog.set_icon_name('dialog-password')
    dialog.set_markup(message)

    result = dialog.run()
    dialog.destroy()
