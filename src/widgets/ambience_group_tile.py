# ambience_group_tile.py
#
# Copyright 2022 Luka Jankovic
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

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ambience_group_tile.ui')
class AmbienceGroupTile(Gtk.FlowBoxChild):
    __gtype_name__ = 'AmbienceGroupTile'

    label = ""
    online = []

    clicked_callback = None

    top_label = Gtk.Template.Child()
    bottom_label = Gtk.Template.Child()

    tile_button = Gtk.Template.Child()

    def __init__(self, group, clicked_callback, **kwargs):
        super().__init__(**kwargs)

        self.group = group
        self.clicked_callback = clicked_callback
        self.top_label.set_text("All lights")

    def count_on(self):
        count = 0
        for device in self.group.get_devices():
            if hasattr(device, "power") and device.power: 
                count += 1
        return count

    def update(self):
        count = self.count_on()
        self.bottom_label.set_text(str(count) + "/" + str(len(self.group.get_devices())) + " lights on")

    @Gtk.Template.Callback("tile_clicked")
    def tile_clicked(self, sender):
        if self.clicked_callback:
            self.clicked_callback(self)
