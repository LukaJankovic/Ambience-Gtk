# sidebar.py
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

from gi.repository import Gtk, GLib, GObject
from lifxlan import *

@Gtk.Template(resource_path='/org/lukjan/ambience/ui/sidebar.ui')
class SidebarListItem(Gtk.ListBoxRow):
    __gtype_name__ = 'SidebarListItem'

    light_label  = Gtk.Template.Child()
    light_switch = Gtk.Template.Child()

    light = None

    @Gtk.Template.Callback("activate_switch")
    def activate_switch(self, sender, user_data):
        if isinstance(self.light, Device):
            self.light.set_power(sender.get_active())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
