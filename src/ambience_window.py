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

from gi.repository import Gtk, GLib, Handy
from .ambience_light_tile import *
from .ambience_settings import *
from .discovery_item import *
from .product_list import *
from .helpers import *
import json, threading

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

    group_header_bar = Gtk.Template.Child()
    back = Gtk.Template.Child()
    title_label = Gtk.Template.Child()

    header_deck = Gtk.Template.Child()
    content_deck = Gtk.Template.Child()
    tiles_list = Gtk.Template.Child()
    light_stack = Gtk.Template.Child()

    light_label = Gtk.Template.Child()
    light_sub_label = Gtk.Template.Child()

    power_switch = Gtk.Template.Child()

    hue_row = Gtk.Template.Child()
    saturation_row = Gtk.Template.Child()
    kelvin_row = Gtk.Template.Child() 
    infrared_row = Gtk.Template.Child()

    hue_scale = Gtk.Template.Child()
    saturation_scale = Gtk.Template.Child()
    brightness_scale = Gtk.Template.Child()
    kelvin_scale = Gtk.Template.Child()
    kelvin_adj = Gtk.Template.Child()
    infrared_scale = Gtk.Template.Child()

    ip_label = Gtk.Template.Child()
    group_label = Gtk.Template.Child()
    location_label = Gtk.Template.Child()

    edit = Gtk.Template.Child()
    edit_stack = Gtk.Template.Child()
    light_edit_label = Gtk.Template.Child()

    lan = None
    lights = []
    offline_lights = []
    in_light = False

    active_row = None
    update_active = False

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

        self.folded = self.content_box.get_folded()

        if self.folded:
            self.back.show_all()
            self.sidebar.unselect_all()
        else:
            self.back.hide()
            self.sidebar.select_row(self.active_row)

        self.header_bar.set_show_close_button(self.folded)

    @Gtk.Template.Callback("go_back")
    def go_back(self, sender):
        """
        Back button pressed. Either goes back to tiles view or group list.
        """

        if self.in_light:
            self.update_tiles()

            self.content_deck.navigate(Handy.NavigationDirection.BACK)
            self.header_deck.navigate(Handy.NavigationDirection.BACK)

            self.in_light = False
        else:
            self.active_group = None
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

    def update_tiles(self):
        for group_item in self.tiles_list.get_children():
            if isinstance(group_item, AmbienceFlowBox):
                for tile in group_item.get_children()[0].get_children():
                    tile.update()

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
        self.content_deck.set_visible_child_name("tiles")
        self.clear_tiles()

        startup_thread = threading.Thread(target=self.startup)
        startup_thread.daemon = True
        startup_thread.start()

    def get_active_lights(self, devices):
        
        online = []
        offline = []

        for light in devices:

            light_item = Light(light["mac"], light["ip"])

            try:
                light_item.get_info_tuple()
                online.append(light_item)
            except WorkflowException:
                light_item.label = light["label"]
                offline.append(light_item)

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

        light_check_thread = threading.Thread(target=self.group_light_check_thread) 
        light_check_thread.daemon = False
        light_check_thread.start()

    def group_light_check_thread(self):
        (self.online, self.offline) = self.get_active_lights(self.group_lights)
        GLib.idle_add(self.set_active_group_ui)

    def set_active_group_ui(self):
        if not self.active_row.group["label"] == "Unknown Group":
            all_tiles = AmbienceFlowBox()
            all_tile = AmbienceLightTile(None)
            all_tile.top_label.set_text("All Lights")

            all_tiles.insert(all_tile, -1)

            self.tiles_list.add(all_tiles)

            lights_on = 0

            if len(self.online) > 0:
                lights_label = self.create_header_label()
                lights_label.set_text("Lights")

                self.tiles_list.add(lights_label)

                lights_tiles = AmbienceFlowBox()

                for light in self.group_lights:
                    light_item = Light(light["mac"], light["ip"])
                    if light_item.get_power():
                        lights_on += 1 

                    flow_item = AmbienceLightTile(light_item)
                    flow_item.clicked_callback = self.tile_clicked
                    lights_tiles.insert(flow_item, -1)

                self.tiles_list.add(lights_tiles)

            sub_text = ""

            if lights_on == 0:
                sub_text = "No lights on"
            elif lights_on == 1:
                sub_text = "1 light on"
            else:
                sub_text = str(lights_on) + "lights on"

            all_tile.bottom_label.set_text(sub_text)

        if len(self.offline) > 0:
            offline_label = self.create_header_label()
            offline_label.set_text("Offline")

            self.tiles_list.add(offline_label)

            lights_tiles = AmbienceFlowBox()

            for light in self.offline:
                flow_item = AmbienceLightTile(None)
                flow_item.top_label.set_text(light.label)
                flow_item.set_sensitive(False)
                lights_tiles.insert(flow_item, -1)

            self.tiles_list.add(lights_tiles)

        self.header_box.set_visible_child(self.header_deck)
        self.refresh_stack.set_visible_child_name("refresh")


    # Light control

    def tile_clicked(self, tile):
        """
        Runs when a tile gets clicked. Switches to the light control page.
        """
        self.content_deck.navigate(Handy.NavigationDirection.FORWARD)
        self.header_deck.navigate(Handy.NavigationDirection.FORWARD)

        self.active_light = tile.light
        self.in_light = True
        self.update_active = True

        self.light_stack.set_visible_child_name("loading")

        fetch_thread = threading.Thread(target=self.fetch_light_data)
        fetch_thread.daemon = False
        fetch_thread.start()

    def fetch_light_data(self):
        self.active_light.label = self.active_light.get_label()
        self.active_light.product = self.active_light.get_product()
        self.active_light.power = self.active_light.get_power()

        self.active_light.has_color = self.active_light.supports_color()
        self.active_light.has_temp = self.active_light.supports_temperature()
        self.active_light.has_infrar = self.active_light.supports_infrared()

        (hue, saturation, brightness, temperature) = self.active_light.get_color()

        self.active_light.brightness = decode(brightness)
        
        if self.active_light.has_color:
            self.active_light.hue = decode_circle(hue)
            self.active_light.saturation = decode(saturation)

        if self.active_light.has_temp:
            self.active_light.temperature = temperature

        if self.active_light.has_infrar:
            self.active_light.infrared = decode(self.active_light.get_infrared())

        self.active_light.ip = self.active_light.get_ip_addr()
        self.active_light.group = self.active_light.get_group_label()
        self.active_light.location = self.active_light.get_location_label()

        GLib.idle_add(self.show_light_controls)

    def show_light_controls(self):
        self.light_label.set_text(self.active_light.label)

        if product_info := self.plist_downloader.get_product(self.active_light.product):
            self.light_sub_label.set_text(product_info["name"])

        self.power_switch.set_active(self.active_light.power)

        self.brightness_scale.set_value(self.active_light.brightness)

        if self.active_light.has_color:
            self.hue_row.set_visible(True)
            self.saturation_row.set_visible(True)

            self.hue_scale.set_value(self.active_light.hue)
            self.saturation_scale.set_value(self.active_light.saturation)

        if self.active_light.has_temp:
            self.kelvin_row.set_visible(True)
            self.kelvin_scale.set_value(self.active_light.temperature)

        if self.active_light.has_infrar:
            self.infrared_row.set_visible(True)
            self.infrared_scale.set_value(self.active_light.infrared)

        self.ip_label.set_label(self.active_light.ip)
        self.group_label.set_label(self.active_light.group)
        self.location_label.set_label(self.active_light.location)

        self.update_active = False
        self.light_stack.set_visible_child_name("light")

    @Gtk.Template.Callback("push_color")
    def push_color(self, sender):
        """
        Color data changed by the user, push it to the bulb.
        """
        if self.update_active:
            return

        hue = self.hue_scale.get_value()
        saturation = self.saturation_scale.get_value()
        brightness = self.brightness_scale.get_value()
        kelvin = self.kelvin_scale.get_value()

        self.active_light.set_color((encode_circle(hue),
                                     encode(saturation),
                                     encode(brightness),
                                     kelvin), rapid=True)

        if self.active_light.supports_infrared():
            self.active_light.set_infrared(encode(self.infrared_scale.get_value()))

    @Gtk.Template.Callback("set_light_power")
    def set_light_power(self, sender, user_data):
        if self.active_light:
            self.active_light.set_power(sender.get_active(), rapid=True)

    # Editing label

    @Gtk.Template.Callback("name_changed")
    def name_changed(self, sender):
        """
        Checks to see if the edit toggle button should be disabled if the name
        is empty.
        """
        self.edit.set_sensitive(self.light_edit_label.get_text())

    @Gtk.Template.Callback("name_activate")
    def name_enter(self, sender):
        """
        Perform the same action as when toggling the edit button.
        """

        if self.edit.get_active():
            self.edit.set_active(False)

    @Gtk.Template.Callback("name_event")
    def name_event(self, sender, event):
        """
        User cancelled edit label event.
        """

        if event.keyval == Gdk.KEY_Escape:
            self.light_edit_label.set_text(self.active_light.label)
            self.edit.set_active(False)

    @Gtk.Template.Callback("do_edit")
    def do_edit(self, sender):
        """
        Toggle edit label mode.
        """
        if self.edit.get_active():
            self.light_edit_label.set_text(self.active_light.label)
            self.edit_stack.set_visible_child_name("editing")
        else:
            new_label = self.light_edit_label.get_text()

            self.edit_stack.set_visible_child_name("normal")

            self.active_light.set_label(new_label)
            self.active_light.label = new_label
            self.light_label.set_text(new_label)

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

        self.reload(self)

    def startup(self):
        if get_old_dest_file().query_exists():
            convert_old_config()

        self.update_sidebar()

        self.plist_downloader = product_list()
        self.plist_downloader.download_list()
