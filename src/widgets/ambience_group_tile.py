import gi

gi.require_version('Gtk', '3.0')
# ambience_group_tile.py
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

gi.require_version('Handy', '1')

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

    def __init__(self, group, **kwargs):
        super().__init__(**kwargs)

        self.group = group
        self.top_label.set_text("All lights")
        self.update()

    def count_on(self):
        count = 0
        for light in self.group.online:
            if light.get_power():
                count += 1
        return count

    def update(self):
        count = self.count_on()
        if count == 0:
            self.bottom_label.set_text("No lights on")
        elif count == 1:
            self.bottom_label.set_text("One light on")
        else:
            self.bottom_label.set_text(str(count) + " lights on")

    @Gtk.Template.Callback("tile_clicked")
    def tile_clicked(self, sender):
        if self.clicked_callback:
            self.clicked_callback(self)