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

from struct import error
import threading

from gi.repository import Gtk, GLib, Handy
from .ambience_light_control import *
from .ambience_group_control import *
from .ambience_light_tile import *
from .ambience_group_tile import *
from .ambience_settings import *
from .discovery_item import *
from .product_list import *
from .helpers import *
import threading

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ui/ambience_window.ui')
class AmbienceWindow(Handy.ApplicationWindow):
    """
    Controls almost every aspect of the main window, including maintaining
    a list of lights and controling them.
    """
    __gtype_name__ = 'AmbienceWindow'

    main_popover = Gtk.Template.Child()
    main_leaflet = Gtk.Template.Child()

    title_label = Gtk.Template.Child()

    menu_box = Gtk.Template.Child()
    header_bar = Gtk.Template.Child()
    refresh_stack = Gtk.Template.Child()
    refresh = Gtk.Template.Child()
    refresh_spinner = Gtk.Template.Child()
    sidebar = Gtk.Template.Child()

    group_header_bar = Gtk.Template.Child()
    back = Gtk.Template.Child()

    controls_deck = Gtk.Template.Child()
    tiles_box = Gtk.Template.Child()

    loading_stack = Gtk.Template.Child()
    tiles_list = Gtk.Template.Child()

    lan = None
    lights = []
    offline_lights = []
    in_light = False

    active_row = None

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

        self.folded = sender.get_folded()

        if self.folded:
            self.back.show_all()
        else:
            self.back.hide()
            
            if self.active_row:
                self.sidebar.select_row(self.active_row)

        self.header_bar.set_show_close_button(self.folded)

    @Gtk.Template.Callback("go_back")
    def go_back(self, sender):
        """
        Back button pressed. Either goes back to tiles view or group list.
        """
        self.sidebar.unselect_all()
        self.main_leaflet.set_visible_child(self.menu_box)

    @Gtk.Template.Callback("sidebar_selected")
    def sidebar_selected(self, sender, user_data):
        """
        Group in sidebar selected by user.
        """

        self.controls_deck.set_visible_child_name("tiles")
        for child in self.controls_deck.get_children()[1:]:
            self.controls_deck.remove(child)

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

        config = get_config(get_dest_file())

        # Check for offline lights with no group
        for group in config["groups"]:
            if group["label"] == "Unknown Group":
                for light in group["lights"]:
                    try:
                        light_item = Light(light["mac"], light["ip"])
                        light_group = light_item.get_group_label()
                        group["lights"].remove(light)
                        config = add_light_to_group(config, light_group, light)                 
                    except WorkflowException:
                        pass

                if len(group["lights"]) == 0:
                    config["groups"].remove(group)

                break

        write_config(config, get_dest_file())
        self.groups = config["groups"]

        GLib.idle_add(self.build_group_list)

    def build_group_list(self):
        for group in self.groups:
            group_item = Handy.ActionRow() # TODO: Add power switch
            group_item.set_visible(True)
            group_item.group = group
            group_item.set_title(group["label"])
            self.sidebar.insert(group_item, -1)

        self.refresh_stack.set_visible_child_name("refresh")

    @Gtk.Template.Callback("reload")
    def reload(self, sender):
        """
        Restart discovery or repopulate the sidebar.
        """
        self.refresh_stack.set_visible_child_name("loading")
        self.clear_tiles()

        startup_thread = threading.Thread(target=self.startup)
        startup_thread.daemon = True
        startup_thread.start()

    def get_active_lights(self, devices):
        
        online = []
        offline = []
        threads = []

        for light in devices:
            light_item = Light(light["mac"], light["ip"])

            def finished(finished_light, success, label):
                if success:
                    online.append(finished_light)
                else:
                    finished_light.label = label
                    offline.append(finished_light)

            fetch_thread = threading.Thread(target=fetch_all_data,
                                            args=(light_item, finished),
                                            kwargs={'data':light["label"]})
            fetch_thread.daemon = False 
            fetch_thread.start()
            threads.append(fetch_thread)
                
        for thread in threads:
            thread.join()

        return (online, offline)

    def set_active_group(self):
        """
        User selected a group. Shows all related lights, presets and other controls.
        """
        if not self.sidebar.get_selected_row():
            return

        self.active_row = self.sidebar.get_selected_row()
        self.title_label.set_text(self.active_row.group["label"])

        self.clear_tiles()
        self.refresh_stack.set_visible_child_name("loading")

        self.group_lights = self.active_row.group["lights"]

        self.main_leaflet.set_visible_child(self.controls_deck)

        if self.folded:
            self.loading_stack.set_visible_child_name("loading")

        light_check_thread = threading.Thread(target=self.group_light_check_thread) 
        light_check_thread.daemon = True 
        light_check_thread.start()

    def group_light_check_thread(self):
        (self.online, self.offline) = self.get_active_lights(self.group_lights)

        self.active_light_count = 0
        for light in self.online:
            if light.power:
                self.active_light_count += 1

        GLib.idle_add(self.set_active_group_ui)

    def set_active_group_ui(self):
        if not self.active_row.group["label"] == "Unknown Group":
            all_tiles = AmbienceFlowBox()
            self.all_tile = AmbienceGroupTile(self.active_row.group["label"], self.online)
            self.all_tile.clicked_callback = self.group_edit
            all_tiles.insert(self.all_tile, -1)

            self.tiles_list.add(all_tiles)

            if len(self.online) > 0:
                lights_label = self.create_header_label()
                lights_label.set_text("Lights")

                self.tiles_list.add(lights_label)

                lights_tiles = AmbienceFlowBox()

                for light in self.online:
                    flow_item = AmbienceLightTile(light)
                    flow_item.clicked_callback = self.tile_clicked
                    lights_tiles.insert(flow_item, -1)

                TEST = False

                if TEST:
                    test_item = AmbienceLightTile(None)
                    test_item.top_label.set_text("Workspace Lamp")
                    test_item.bottom_label.set_text("Off")

                    lights_tiles.insert(test_item, -1)

                self.tiles_list.add(lights_tiles)

        if len(self.offline) > 0:
            offline_label = self.create_header_label()
            offline_label.set_text("Offline")

            self.tiles_list.add(offline_label)

            lights_tiles = AmbienceFlowBox()

            for light in self.offline:
                flow_item = AmbienceLightTile(None, False)
                flow_item.top_label.set_text(light.label)
                flow_item.set_sensitive(False)
                lights_tiles.insert(flow_item, -1)

            self.tiles_list.add(lights_tiles)

        self.refresh_stack.set_visible_child_name("refresh")
        self.loading_stack.set_visible_child_name("tiles")

    # Light control

    def tile_clicked(self, tile):
        """
        Runs when a tile gets clicked. Switches to the light control page.
        """
        light_controls = AmbienceLightControl(tile.light,
                                              self.controls_deck,
                                              self.plist_downloader,
                                              self.light_control_exit)
        light_controls.set_visible(True)

        self.controls_deck.insert_child_after(light_controls, self.tiles_box)
        self.controls_deck.navigate(Handy.NavigationDirection.FORWARD)
        light_controls.show()

    def group_edit(self):
        group_controls = AmbienceGroupControl(self.active_row.group,
                                              self.online,
                                              self.controls_deck,
                                              self.light_control_exit)

        group_controls.set_visible(True)

        self.controls_deck.insert_child_after(group_controls, self.tiles_box)
        self.controls_deck.navigate(Handy.NavigationDirection.FORWARD)
        group_controls.show()

    def light_control_exit(self, controls):
        self.controls_deck.navigate(Handy.NavigationDirection.BACK)
        self.remove_request = controls
        self.set_active_group()

    def transition_update(self, sender, user_data):
        if not sender.get_transition_running() and self.remove_request is not None:
            sender.remove(self.remove_request)
            self.remove_request = None

    # Group management
    def get_group_value(self, prop):
        value = -1
        for light in self.online:
            if value == -1:
                value = light.__dict__[prop]
            elif not value == light.__dict__[prop]:
                break

        if value == -1:
            return None
        return value

    # Initialization, startup

    def __init__(self, lan, **kwargs):
        """
        Check if LifxLAN api available, small ui initialization.
        """

        super().__init__(**kwargs)

        if not API_AVAIL or not lan:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="LifxLAN api not found"
            )

            dialog.format_secondary_text(
                "Please install lifxlan using pip then relaunch Ambience."
            )

            dialog.run()
            dialog.destroy()
            exit(1)

        self.lan = lan


        self.reload(self)

    def startup(self):
        if get_old_dest_file().query_exists():
            convert_old_config()
            move_old_config()

        self.update_sidebar()

        self.plist_downloader = product_list()
        self.plist_downloader.download_list()
