# ambience_window.py
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

import threading

try:
    import lifxlan
    API_AVAIL = True
except ImportError:
    API_AVAIL = False

from gi.repository import Gtk, Gdk, GLib, GObject, Handy
from .ambience_light_tile import *
from .discovery_item import *
from .product_list import *
import json

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

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ui/ambience_window.ui')
class AmbienceWindow(Handy.ApplicationWindow):
    """
    Controls almost every aspect of the main window, including maintaining
    a list of lights and controling them.
    """
    __gtype_name__ = 'AmbienceWindow'

    main_popover = Gtk.Template.Child()

    title_bar = Gtk.Template.Child()
    header_box = Gtk.Template.Child()
    content_box = Gtk.Template.Child()

    menu = Gtk.Template.Child()
    header_bar = Gtk.Template.Child()
    refresh_stack = Gtk.Template.Child()
    refresh = Gtk.Template.Child()
    refresh_spinner = Gtk.Template.Child()
    sidebar = Gtk.Template.Child()

    sub_header_bar = Gtk.Template.Child()
    back = Gtk.Template.Child()
    title_label = Gtk.Template.Child()

    tiles_list = Gtk.Template.Child()

    lan = None
    lights = []
    d_lights = []

    active_row = None
    update_active = False

    def get_lights(self, config):
        lights = []
        for light in config:
            light_item = Light(light["mac"], light["ip"])
            light_item.offline_conf = light

            try:
                light_item.get_power() # "Ping"
                light_item.online = True
            except WorkflowException:
                light_item.online = False

            lights.append(light_item)

        return lights
                

    def get_groups(self, lights):
        """
        Discovers groups from list of lights
        """

        groups = []

        for light in lights:

            group_label = ""
            try:
                group_label = light.get_group_label()
            except WorkflowException:
                group_label = light.offline_conf["group"]
                # TODO: Check for old config

            if group_label not in [x.label for x in groups]:
                group = self.lan.get_devices_by_group(group_label)
                group.label = group_label
                groups.append(group)

        return groups

    # Misc. File Management

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

    # Misc. Window / UI Management

    def create_header_label(self):
        """
        Returns a GtkLabel suitable to be used as a header in the tiles list.
        """
        label = Gtk.Label()
        label.get_style_context().add_class("title-3")
        label.set_visible(True)
        label.set_margin_start(6)
        label.set_margin_end(6)
        label.set_margin_top(6)
        label.set_margin_bottom(6)
        label.set_alignment(0, 0)

        return label

    @Gtk.Template.Callback("notify_fold_cb")
    def notify_fold_cb(self, sender, user_data):
        """
        Window switched between normal and mobile (folded) state.
        """

        folded = self.content_box.get_folded()

        if folded:
            self.back.show_all()

            self.sidebar.unselect_all()
        else:
            self.back.hide()
            self.sidebar.select_row(self.active_row)

        self.header_bar.set_show_close_button(folded)

    @Gtk.Template.Callback("go_back")
    def go_back(self, sender):
        """
        Back button in folded mode pressed.
        """

        self.active_light = None
        self.sidebar.unselect_all()
        self.content_box.set_visible_child(self.menu)
        self.header_box.set_visible_child(self.header_bar)

    @Gtk.Template.Callback("sidebar_selected")
    def sidebar_selected(self, sender, user_data):
        """
        Group in sidebar selected by user.
        """

        self.set_active_group()

    def clear_sidebar(self):
        """
        Empties the sidebar.
        """

        for sidebar_item in self.sidebar.get_children():
            self.sidebar.remove(sidebar_item)

    def clear_tiles(self):
        """
        Empties the main view from tiles, headers, etc.
        """

        for group_item in self.tiles_list.get_children():
            self.tiles_list.remove(group_item)

    def update_sidebar(self):
        """
        Repopulates groups and rebuilds group list.
        """

        self.refresh_stack.set_visible_child_name("loading")
        self.clear_sidebar()

        config = self.get_config()
        self.lights = self.get_lights(config)
        self.groups = self.get_groups(self.lights)

        for group in self.groups:
            group_item = Handy.ActionRow() # TODO: Add power switch
            group_item.set_visible(True)
            group_item.group = group
            group_item.set_title(group.label)
            self.sidebar.insert(group_item, -1)

        self.refresh_stack.set_visible_child_name("refresh")

    @Gtk.Template.Callback("reload")
    def reload(self, sender):
        """
        Restart discovery or repopulate the sidebar.
        """
        self.update_sidebar()

    def set_active_group(self):
        """
        User selected a group. Shows all related lights, presets and other controls.
        """
        if not self.sidebar.get_selected_row():
            return

        self.active_row = self.sidebar.get_selected_row()
        self.title_label.set_text(self.active_row.group.label)

        self.clear_tiles()

        all_tiles = AmbienceFlowBox()
        all_tile = AmbienceLightTile(None)
        all_tile.top_label.set_text("All Lights")
        all_tiles.insert(all_tile, -1)

        self.tiles_list.add(all_tiles)

        lights_label = self.create_header_label()
        lights_label.set_text("Lights")

        self.tiles_list.add(lights_label)

        lights_tiles = AmbienceFlowBox()

        for light in self.active_row.group.get_device_list():
            flow_item = AmbienceLightTile(light)
            lights_tiles.insert(flow_item, -1)

        self.tiles_list.add(lights_tiles)

        self.header_box.set_visible_child(self.sub_header_bar)

    def __init__(self, lan, **kwargs):
        """
        Check if LifxLAN api available, small ui initialization.
        """

        super().__init__(**kwargs)
        self.lan = lan

        if not API_AVAIL:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="LifxLAN api not found"
            )

            dialog.format_secondary_text(
                "Please install using pip then relaunch Ambience."
            )

            dialog.run()
            dialog.destroy()
            exit(1)

        self.update_sidebar()

        self.plist_downloader = product_list()
        self.plist_downloader.download_list()
