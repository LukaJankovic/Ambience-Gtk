# ambience_discovery_item.py
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

from gi.repository import Gtk

from ambience.ambience_loader import AmbienceLoader

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ambience_discovery_item.ui')
class AmbienceDiscoveryItem(Gtk.ListBoxRow):
    """
    Sidebar item when in discovery mode. Contains a toggle box instead of a
    power switch which is used to add the bulb to the main list.
    """

    __gtype_name__ = 'AmbienceDiscoveryItem'

    device_label  = Gtk.Template.Child()
    add_btn      = Gtk.Template.Child()
    add_img      = Gtk.Template.Child()

    device = None
    added = False
    dest_file = None
    config_list = []

    def update_icon(self):
        """
        Makes sure the icon shown in the toggle button matches the current
        state of the bulb.
        """

        if self.added:
            self.add_img.set_from_icon_name("emblem-ok-symbolic", Gtk.IconSize.BUTTON)
        else:
            self.add_img.set_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)

    @Gtk.Template.Callback("add_clicked")
    def add_clicked(self, sender):
        """
        Add or remove the bulb to the main list.
        """

        group = AmbienceLoader().get_group(self.device.get_lifx_group_label())
        if self.added:
            AmbienceLoader().remove_device(self.device, group=group)
        else:
            AmbienceLoader().add_device(group, self.device)

        self.added = not self.added

        self.update_icon()

    def __init__(self, device, **kwargs):
        super().__init__(**kwargs)

        self.device = device 
        self.device_label.set_label(self.device.get_label())

        if AmbienceLoader().has_device(self.device):
            self.added = True

        self.update_icon()