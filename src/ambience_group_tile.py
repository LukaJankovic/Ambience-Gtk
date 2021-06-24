import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')

from gi.repository import Gtk, GLib
from lifxlan import *
import threading

from .helpers import *

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ui/ambience_group_tile.ui')
class AmbienceGroupTile(Gtk.FlowBoxChild):
    __gtype_name__ = 'AmbienceGroupTile'

    label = ""
    online = []

    clicked_callback = None

    top_label = Gtk.Template.Child()
    bottom_label = Gtk.Template.Child()

    tile_button = Gtk.Template.Child()

    def __init__(self, label, online, **kwargs):
        super().__init__(**kwargs)

        self.label = label
        self.online = online

        self.top_label.set_text("All lights")

        self.update()

    def count_on(self):
        count = 0
        for light in self.online:
            if light.power:
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
            self.clicked_callback()