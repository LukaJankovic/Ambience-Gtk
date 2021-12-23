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
from ambience.widgets.ambience_discovery_item import AmbienceDiscoveryItem

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ambience_discovery.ui')
class AmbienceDiscovery(Gtk.Dialog):
    __gtype_name__ = 'AmbienceDiscovery'

    subheader = Gtk.Template.Child()
    reload_stack = Gtk.Template.Child()
    device_spinner = Gtk.Template.Child()

    main_deck = Gtk.Template.Child()
    providers_list = Gtk.Template.Child()
    devices_list = Gtk.Template.Child()

    providers = AmbienceProviders()
    current_provider = None

    @Gtk.Template.Callback("provider_selected")
    def provider_selected(self, sender, user_data):
        selected_row = sender.get_selected_row()
        
        if not selected_row:
            return

        provider = AmbienceProviders().import_provider(selected_row.provider)

        self.main_deck.set_visible_child_name("devices")
        self.subheader.set_title(self.providers.get_name_for_provider(selected_row.provider))

        self.current_provider = provider
        self.reload_devices(self)

    @Gtk.Template.Callback("reload_devices")
    def reload_devices(self, sender):

        self.reload_stack.set_visible_child_name("loading")
        self.device_spinner.start()

        for item in self.devices_list.get_children():
            self.devices_list.remove(item)

        def set_devices():
            devices = self.current_provider.discovery_list()

            def update_list():
                for device in devices: 
                    row = AmbienceDiscoveryItem(device)
                    row.set_visible(True)

                    self.devices_list.insert(row, -1)

                self.providers_list.unselect_all()
                self.reload_stack.set_visible_child_name("button")

            GLib.idle_add(update_list)

        discovery_thread = threading.Thread(target=set_devices)
        discovery_thread.start()

        #AmbienceProviders().unimport_provider(provider) ??

    @Gtk.Template.Callback("go_back")
    def go_back(self, sender):
        self.providers_list.unselect_all()
        self.main_deck.set_visible_child_name("providers")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        for provider in self.providers.get_provider_list():
            row = Handy.ActionRow()
            row.set_title(self.providers.get_name_for_provider(provider))
            row.provider = provider

            img = Gtk.Image.new_from_icon_name("go-next-symbolic", 0)
            img.set_visible(True)
            
            row.add(img)
            self.providers_list.insert(row, -1)
