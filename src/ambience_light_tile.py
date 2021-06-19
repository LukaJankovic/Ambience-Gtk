import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')

from gi.repository import Gtk, Gdk, Gio, Handy
import colorsys
import lifxlan

from .helpers import *

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ui/ambience_flow_box.ui')
class AmbienceFlowBox(Gtk.Box):
    __gtype_name__ = 'AmbienceFlowBox'

    flowbox = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def insert(self, item, index):
        self.flowbox.insert(item, index)

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ui/ambience_light_tile.ui')
class AmbienceLightTile(Gtk.FlowBoxChild):
    __gtype_name__ = 'AmbienceLightTile'

    light = None

    button_style_provider = None
    text_style_provider = None

    clicked_callback = None

    top_label = Gtk.Template.Child()
    bottom_label = Gtk.Template.Child()

    tile_button = Gtk.Template.Child()

    def __init__(self, light, online=True, **kwargs):
        super().__init__(**kwargs)

        if light and online:
            self.light = light

        self.update()

    def update(self):

        if not self.light:
            return

        (hue, saturation, brightness, temperature) = self.light.get_color()

        self.top_label.set_text(self.light.get_label())

        if self.button_style_provider:
            self.tile_button.get_style_context().remove_provider(self.button_style_provider)

        if self.light.get_power():
            self.bottom_label.set_text(str(int(decode(brightness))) + "%")
            (r, g, b) = colorsys.hsv_to_rgb(int(decode_circle(hue)), decode(saturation) / 100, decode(brightness) / 100)

            css = f'.ambience_light_tile {{ background: { rgb_to_hex(r, g, b) }; }}'.encode()
            self.button_style_provider = Gtk.CssProvider()
            self.button_style_provider.load_from_data(css)

            self.tile_button.get_style_context().add_provider(self.button_style_provider, 600) # TODO: fix magic number

        if self.text_style_provider:
            self.top_label.get_style_context().remove_provider(self.text_style_provider)
            self.bottom_label.get_style_context().remove_provider(self.text_style_provider)
            self.text_style_provider = None

        if self.light.get_power():

            css = '.ambience_light_tile_text { color: #FFFFFF; }'.encode()

            if (int(r * 255) * 0.299 + int(g * 255) * 0.587 + int(b * 255) * 0.114) > 186:
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