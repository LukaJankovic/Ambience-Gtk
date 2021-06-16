from gi.repository import Gtk, Gdk, GLib, GObject, Handy
import threading, json

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

    def get_dest_file(self):
        """
        Create / find the file used to store lights.
        """

        data_dir = GLib.get_user_config_dir()
        dest = GLib.build_filenamev([data_dir, "lights.json"])
        return Gio.File.new_for_path(dest)

    def get_config(self):
        """
        Loads the config file into a dictionary.
        """

        dest_file = self.get_dest_file()

        try:
            (success, content, tag) = dest_file.load_contents()
            return json.loads(content.decode("utf-8"))
        except GLib.GError as error:
            # File doesn't exist
            dest_file.create(Gio.FileCopyFlags.NONE, None)
        except (TypeError, ValueError) as e:
            # File is most likely empty
            print("Config file empty")
        return []

    def discovery(self):
        """
        Discovery thread.
        """

        self.lights = self.lan.get_lights()
        GLib.idle_add(self.update_list)

    def update_list(self):
        config_list = self.get_config()

        for light in self.lights:
            sidebar_item = DiscoveryItem()
            sidebar_item.light = light
            sidebar_item.light_label.set_text(light.get_label())
            sidebar_item.dest_file = self.get_dest_file()
            sidebar_item.config_list = config_list

            for saved_light in config_list:
                if saved_light["mac"] == light.get_mac_addr():
                    sidebar_item.added = True
                    sidebar_item.update_icon()
                    break

            self.list_box.insert(sidebar_item, -1)