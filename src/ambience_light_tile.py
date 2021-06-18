import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')

from gi.repository import Gtk, Gdk, Gio, Handy
import colorsys
import lifxlan

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ui/ambience_flow_box.ui')
class AmbienceFlowBox(Gtk.Box):
    __gtype_name__ = 'AmbienceFlowBox'

    flowbox = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def insert(self, item, index):
        self.flowbox.insert(item, index)

# Helper functions for converting values to / from api
def decode(nr):
    """
    Convert from 16 bit unsigned integer to range between 0 and 100.
    """
    return (nr / 65535) * 100

def decode_circle(nr):
    """
    Convert from 16 bit unsined integer to range between 0 and 365.
    """
    return (nr / 65535) * 365

def encode(nr):
    """
    Convert from range 0 to 100 to 16 bit unsigned integer limit
    """
    return (nr / 100) * 65535

def encode_circle(nr):
    """
    Convert from range 0 to 365 to 16 bit unsigned integer limit
    """
    return (nr / 365) * 65535

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))


@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ui/ambience_light_tile.ui')
class AmbienceLightTile(Gtk.FlowBoxChild):
    __gtype_name__ = 'AmbienceLightTile'

    light = None
    button_style_provider = None
    text_style_provider = None

    top_label = Gtk.Template.Child()
    bottom_label = Gtk.Template.Child()

    tile_button = Gtk.Template.Child()

    def __init__(self, light, **kwargs):
        super().__init__(**kwargs)

        if light:
            self.light = light
            self.update()

    def update(self):
        (hue, saturation, brightness, temperature) = self.light.get_color()

        self.top_label.set_text(self.light.get_label())
        self.bottom_label.set_text(str(int(decode(brightness))) + "%")

        if self.button_style_provider:
            self.tile_button.get_style_context().remove_provider(self.button_style_provider)

        (r, g, b) = colorsys.hsv_to_rgb(int(decode_circle(hue)), decode(saturation) / 100, decode(brightness) / 100)

        css = f'.ambience_light_tile {{ background: { rgb_to_hex(r, g, b) }; }}'.encode()
        self.button_style_provider = Gtk.CssProvider()
        self.button_style_provider.load_from_data(css)

        self.tile_button.get_style_context().add_provider(self.button_style_provider, 600) # TODO: fix magic number

        if self.text_style_provider:
            self.top_label.get_style_context().remove_provider(self.text_style_provider)
            self.bottom_label.get_style_context().remove_provider(self.text_style_provider)
            self.text_style_provider = None

        if (int(r * 255) * 0.299 + int(g * 255) * 0.587 + int(b * 255) * 0.114) > 186:
            css = '.ambience_light_tile_text { color: #000000; }'.encode()

            self.text_style_provider = Gtk.CssProvider()
            self.text_style_provider.load_from_data(css)

            self.top_label.get_style_context().add_provider(self.text_style_provider, 600)
            self.bottom_label.get_style_context().add_provider(self.text_style_provider, 600)