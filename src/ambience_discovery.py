from gi.repository import Gtk, Gdk, GLib, GObject, Handy
import threading, json

from .ambience_settings import *
from .discovery_item import *

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ui/ambience_discovery.ui')
class AmbienceDiscovery(Gtk.Dialog):
    __gtype_name__ = 'AmbienceDiscovery'

    list_box = Gtk.Template.Child()
    lan = None

    def __init__(self, lan, **kwargs):
        super().__init__(**kwargs)
        self.lan = lan

        self.init_discovery()

    def init_discovery(self):
        """
        Initialize discovery thread. Starts spinner etc.
        """
        discovery_thread = threading.Thread(target=self.discovery)
        discovery_thread.daemon = True
        discovery_thread.start()

    def discovery(self):
        """
        Discovery thread.
        """

        self.lights = self.lan.get_lights()
        GLib.idle_add(self.update_list)

    def update_list(self):
        config_list = get_config(get_dest_file())

        for light in self.lights:
            sidebar_item = DiscoveryItem()
            sidebar_item.light = light
            sidebar_item.light_label.set_text(light.get_label())
            sidebar_item.dest_file = get_dest_file()
            sidebar_item.config_list = config_list

            done = False
            for group in config_list["groups"]:
                for saved_light in group["lights"]:
                    if saved_light["mac"] == light.get_mac_addr():
                        sidebar_item.added = True
                        sidebar_item.update_icon()
                        done = True
                        break

                if done:
                    break

            self.list_box.insert(sidebar_item, -1)