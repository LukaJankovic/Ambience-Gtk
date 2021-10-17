# ambience_discovery.py
#
# Copyright 2021 Luka Jankovic
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

from gi.repository import Gtk, Gdk, GLib, GObject, Handy
import threading, json

from ambience.providers.ambience_providers import AmbienceProviders

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ambience_discovery.ui')
class AmbienceDiscovery(Gtk.Dialog):
    __gtype_name__ = 'AmbienceDiscovery'

    menu = Gtk.Template.Child()

    providers = AmbienceProviders()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        for provider in self.providers.get_provider_list():
            row = Handy.ActionRow()
            row.set_title(self.providers.get_name_for_provider(provider))

            img = Gtk.Image.new_from_icon_name("go-next-symbolic", 0)
            img.set_visible(True)
            
            row.add(img)
            self.menu.insert(row, -1)
