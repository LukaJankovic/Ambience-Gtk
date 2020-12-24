# discovery_item.py
#
# Copyright 2020 Luka Jankovic
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, GLib, GObject, Gio
from lifxlan import *
import json

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ui/discovery_item.ui')
class DiscoveryItem(Gtk.ListBoxRow):
    __gtype_name__ = 'DiscoveryItem'

    light_label  = Gtk.Template.Child()
    add_btn      = Gtk.Template.Child()
    add_img      = Gtk.Template.Child()

    light = None
    added = False
    dest_file = None
    config_list = []

    def update_icon(self):
        if self.added:
            self.add_img.set_from_icon_name("emblem-ok-symbolic", Gtk.IconSize.BUTTON)
        else:
            self.add_img.set_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)

    def add_clicked(self, sender):

        permissions = 0o664

        if self.added:
            for light in self.config_list:
                if light["mac"] == self.light.get_mac_addr():
                    self.config_list.remove(light)
                    self.added = False
        else:
            self.config_list.append({"ip":      self.light.get_ip_addr(),
                                    "mac":      self.light.get_mac_addr(),
                                    "label":    self.light.get_label()})
            self.added = True

        if GLib.mkdir_with_parents(self.dest_file.get_parent().get_path(), permissions) == 0:
            (success, tag) = self.dest_file.replace_contents(str.encode(json.dumps(self.config_list)), None, False, Gio.FileCreateFlags.REPLACE_DESTINATION, None)

            if success:
                self.update_icon()
            else:
                print("Unable to save config file")
        else:
            print("Unable to create required directory/ies for config file")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_btn.connect("clicked", self.add_clicked)

