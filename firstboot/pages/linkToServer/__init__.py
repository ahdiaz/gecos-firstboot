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
import urlparse
import gobject
from firstboot_lib import PageWindow, FirstbootEntry

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')


__REQUIRED__ = False

__TITLE__ = _('Link workstation to a server')

__CONFIG_FILE_VERSION__ = '1.1'

__URLOPEN_TIMEOUT__ = 5
__LDAP_BAK_FILE__ = '/etc/ldap.conf.firstboot.bak'
__LDAP_CONF_SCRIPT__ = 'firstboot-ldapconf.sh'

__STATUS_TEST_PASSED__ = 0
__STATUS_CONFIG_CHANGED__ = 1
__STATUS_CONNECTING__ = 2
__STATUS_ERROR__ = 3


def get_page(options=None):

    page = LinkToServerPage(options)
    return page

class LinkToServerPage(PageWindow.PageWindow):
    __gtype_name__ = "LinkToServerPage"

    __gsignals__ = {
        'page-changed': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
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
        self.lblUrl = builder.get_object('lblUrl')
        self.txtUrl = builder.get_object('txtUrl')
        self.imgStatus = builder.get_object('imgStatus')
        self.lblStatus = builder.get_object('lblStatus')
        self.btnLinkToServer = builder.get_object('btnLinkToServer')

        self.show_status()

        container = builder.get_object('ContainerWindow')
        page = builder.get_object('LinkToServerPage')
        container.remove(page)
        self.page = page

        self.translate()

        self.cmd_options = options
        self.fbe = FirstbootEntry.FirstbootEntry()

        url_config = self.fbe.get_url()
        url = self.cmd_options.url

        if url == None or len(url) == 0:
            url = url_config

        if url == None or len(url) == 0:
            url = ''

        self.txtUrl.set_text(url)

    def is_associated(self):
        return os.path.exists(__LDAP_BAK_FILE__)

    def translate(self):
        desc = _('When a workstation is linked to a GECOS server it can be \
managed remotely and existing users in the server can login into \
the workstation.\n\n')

        if not self.is_associated():
            self.btnLinkToServer.set_label(_('Configure'))
            desc_detail = _('For linking this workstation, type the URL where the \
configuration resides and click on "Link".')
        else:
            self.btnLinkToServer.set_label(_('Unlink'))
            desc_detail = _('This workstation is currently linked to a GECOS \
server. If you want to unlink it click on "Unlink".')

        self.lblDescription.set_text(desc + desc_detail)
        self.builder.get_object('radioManual').set_label(_('Manual'))
        self.builder.get_object('radioAuto').set_label(_('Automatic'))

    def get_widget(self):
        return self.page

    def on_txtUrl_changed(self, entry):
        pass

    def get_url(self):
        url = self.txtUrl.get_text()
        parsed_url = list(urlparse.urlparse(url))
        if parsed_url[0] in ('http', 'https'):
            query = urlparse.parse_qsl(parsed_url[4])
            query.append(('v', __CONFIG_FILE_VERSION__))
            query = urllib.urlencode(query)
            parsed_url[4] = query
        url = urlparse.urlunparse(parsed_url)
        return url

    def on_radioManual_toggled(self, button):
        self.lblUrl.set_visible(False)
        self.txtUrl.set_visible(False)

    def on_radioAutomatic_toggled(self, button):
        self.lblUrl.set_visible(True)
        self.txtUrl.set_visible(True)

    def on_btnTest_Clicked(self, button):
        
        self.emit('page-changed', 'MyCustom', [1, 2, 3])
        return

        self.show_status()

        try:
            conf = self.get_conf_from_server()
            self.show_status(__STATUS_TEST_PASSED__)

        except LinkToServerException as e:
            self.show_status(__STATUS_ERROR__, e)

        except Exception as e:
            print e

    def on_btnLinkToServer_Clicked(self, button):

        self.show_status()

        if self.is_associated():
            self.unlink_from_server()

        else:
            self.link_to_server()


    def link_to_server(self):

        try:

            conf = self.get_conf_from_server()

            script = os.path.join('/usr/local/bin', __LDAP_CONF_SCRIPT__)
            if not os.path.exists(script):
                raise LinkToServerException("The file could not be found: " + script)

            cmd = 'gksu "%s %s %s %s"' % (script, str(conf['uri']), str(conf['port']), str(conf['base']))
            args = shlex.split(cmd)

            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exit_code = os.waitpid(process.pid, 0)
            output = process.communicate()[0]

            if exit_code[1] == 0:
                self.show_status(__STATUS_CONFIG_CHANGED__)

            else:
                self.show_status(__STATUS_ERROR__, Exception(_('An error has occurred') + ': ' + output))

        except LinkToServerException as e:
            self.show_status(__STATUS_ERROR__, e)

        except Exception as e:
            self.show_status(__STATUS_ERROR__, Exception(_('An error has occurred')))
            print e

        self.translate()

    def unlink_from_server(self):

        try:

            script = os.path.join('/usr/local/bin', __LDAP_CONF_SCRIPT__)
            if not os.path.exists(script):
                raise LinkToServerException("The file could not be found: " + script)

            cmd = 'gksu "%s --restore"' % (script,)
            args = shlex.split(cmd)

            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exit_code = os.waitpid(process.pid, 0)
            output = process.communicate()[0]

            if exit_code[1] == 0:
                self.show_status(__STATUS_CONFIG_CHANGED__)

            else:
                self.show_status(__STATUS_ERROR__, Exception(_('An error has occurred') + ': ' + output))

        except Exception as e:
            self.show_status(__STATUS_ERROR__, Exception(_('An error has occurred')))
            print e

        self.translate()

    def get_conf_from_server(self):

        self.show_status(__STATUS_CONNECTING__)

        try:

            fp = urllib2.urlopen(self.get_url(), timeout=__URLOPEN_TIMEOUT__)
            #print fp.url(), fp.info()
            content = fp.read()
            conf = json.loads(content)

            if 'version' in conf and 'uri' in conf and 'port' in conf and 'base' in conf:
                version = conf['version']
                if version != __CONFIG_FILE_VERSION__:
                    raise Exception(_('Incorrect version of the configuration file.'))

                return conf

            raise ValueError()

        except urllib2.URLError as e:
            raise LinkToServerException(e.args[0])

        except ValueError as e:
            raise LinkToServerException(_('Configuration file is not valid.'))

        except Exception as e:
            raise Exception(e.args[0])

    def show_status(self, status=None, exception=None):

        icon_size = gtk.ICON_SIZE_BUTTON

        if status == None:
            self.imgStatus.set_visible(False)
            self.lblStatus.set_visible(False)

        elif status == __STATUS_TEST_PASSED__:
            self.imgStatus.set_from_stock(gtk.STOCK_APPLY, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('The configuration file is valid'))
            self.lblStatus.set_visible(True)

        elif status == __STATUS_CONFIG_CHANGED__:
            self.imgStatus.set_from_stock(gtk.STOCK_APPLY, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('The configuration was updated successfully'))
            self.lblStatus.set_visible(True)

        elif status == __STATUS_ERROR__:
            self.imgStatus.set_from_stock(gtk.STOCK_DIALOG_ERROR, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(str(exception.args[0]))
            self.lblStatus.set_visible(True)

        elif status == __STATUS_CONNECTING__:
            self.imgStatus.set_from_stock(gtk.STOCK_CONNECT, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('Trying to connect...'))
            self.lblStatus.set_visible(True)

class LinkToServerException(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)
