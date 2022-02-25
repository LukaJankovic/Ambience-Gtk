# ambience_light_tile.py
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

import gi

from gi.repository import Gtk

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ambience_edit_tile.ui')
class AmbienceEditTile(Gtk.FlowBoxChild):
    __gtype_name__ = 'AmbienceEditTile'

    light = None

    button_style_provider = None
    text_style_provider = None

    clicked_callback = None

    top_label = Gtk.Template.Child()
    select_box = Gtk.Template.Child()

    tile_button = Gtk.Template.Child()

    lock = False

    @Gtk.Template.Callback("tile_clicked")
    def tile_clicked(self, sender):
        if not self.lock:
            self.lock = True
            self.select_box.set_active(not self.select_box.get_active())
            if self.clicked_callback:
                self.clicked_callback(self.light, self.select_box.get_active())
            self.lock = False

    def __init__(self, light, clicked_callback, **kwargs):
        super().__init__(**kwargs)

        self.clicked_callback = clicked_callback
        self.light = light
        self.top_label.set_text(light.label)

        #self.update()