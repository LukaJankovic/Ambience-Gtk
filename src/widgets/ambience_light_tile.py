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
import colorsys

from ambience.model.ambience_light import AmbienceLightCapabilities

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))

def darkmode_color(r, g, b):
    return (int(r * 255) * 0.299 + int(g * 255) * 0.587 + int(b * 255) * 0.114) > 145

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ambience_light_tile.ui')
class AmbienceLightTile(Gtk.FlowBoxChild):
    __gtype_name__ = 'AmbienceLightTile'

    light = None

    button_style_provider = None
    text_style_provider = None

    clicked_callback = None

    top_label = Gtk.Template.Child()
    bottom_label = Gtk.Template.Child()

    tile_button = Gtk.Template.Child()

    def clear_styles(self):
        if self.button_style_provider:
            self.tile_button.get_style_context().remove_provider(self.button_style_provider)

        if self.text_style_provider:
                self.top_label.get_style_context().remove_provider(self.text_style_provider)
                self.bottom_label.get_style_context().remove_provider(self.text_style_provider)
                self.text_style_provider = None

    def update(self):
        self.top_label.set_text(self.light.label)
        self.clear_styles()

        if self.offline:
            self.bottom_label.set_text("Unavailable")
            return

        if AmbienceLightCapabilities.COLOR in self.light.capabilities:
            if self.light.power:
                (h, s, v, k) = self.light.color
                (r, g, b) = colorsys.hsv_to_rgb(h, s, v)

                self.bottom_label.set_text(str(int(v * 100)) + "%")

                css = f'.ambience_light_tile {{ background: { rgb_to_hex(r, g, b) }; }}'.encode()
                self.button_style_provider = Gtk.CssProvider()
                self.button_style_provider.load_from_data(css)

                self.tile_button.get_style_context().add_provider(self.button_style_provider, 600) # TODO: fix magic number

                css = '.ambience_light_tile_text { color: #FFFFFF; }'.encode()

                if darkmode_color(r, g, b):
                    css = '.ambience_light_tile_text { color: #000000; }'.encode()

                self.text_style_provider = Gtk.CssProvider()
                self.text_style_provider.load_from_data(css)

                self.top_label.get_style_context().add_provider(self.text_style_provider, 600)
                self.bottom_label.get_style_context().add_provider(self.text_style_provider, 600)

            else:
                self.bottom_label.set_text("Off")

    @Gtk.Template.Callback("tile_clicked")
    def tile_clicked(self, sender):
        if self.clicked_callback:
            self.clicked_callback(self)

    def __init__(self, light, clicked_callback, offline=False, **kwargs):
        super().__init__(**kwargs)

        self.light = light
        self.clicked_callback = clicked_callback
        self.offline = offline

        self.update()