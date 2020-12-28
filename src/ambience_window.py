# ambience_window.py
#
# Copyright 2020 Luka Jankovic
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
from .light_item import *
from .discovery_item import *
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
    discovery_btn = Gtk.Template.Child()
    sidebar = Gtk.Template.Child()

    content_stack = Gtk.Template.Child()
    sub_header_bar = Gtk.Template.Child()
    edit_stack = Gtk.Template.Child()
    back = Gtk.Template.Child()
    edit = Gtk.Template.Child()
    edit_label = Gtk.Template.Child()
    name_label = Gtk.Template.Child()
    ip_label = Gtk.Template.Child()

    controls_box = Gtk.Template.Child()
    power_row = Gtk.Template.Child()
    power_switch = Gtk.Template.Child()
    hue_scale = Gtk.Template.Child()
    saturation_scale = Gtk.Template.Child()
    brightness_scale = Gtk.Template.Child()
    kelvin_scale = Gtk.Template.Child()

    group_label = Gtk.Template.Child()
    location_label = Gtk.Template.Child()

    lan = None
    lights = []
    d_lights = []

    active_light = None
    discovery_active = False
    update_active = False

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

    @Gtk.Template.Callback("notify_fold_cb")
    def notify_fold_cb(self, sender, user_data):
        """
        Window switched between normal and mobile (folded) state.
        """

        folded = self.content_box.get_folded()

        if folded:
            self.back.show_all()
            self.power_row.show_all()

            self.sidebar.unselect_all()
        else:
            self.back.hide()
            self.power_row.hide()

            self.sidebar.select_row(self.active_light)

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
        Light in sidebar selected.
        """

        self.set_active_light()

    def clear_sidebar(self):
        """
        Empties the sidebar.
        """

        for sidebar_item in self.sidebar.get_children():
            self.sidebar.remove(sidebar_item)

    def update_sidebar(self):
        """
        Repopulates the sidebar. Starts discovery if in discovery mode
        otherwise loads the lights from config.
        """

        self.refresh_stack.set_visible_child_name("loading")
        self.clear_sidebar()

        if self.discovery_active:
            config_list = self.get_config()

            for light in self.d_lights:
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

                self.sidebar.insert(sidebar_item, -1)

        else:
            self.lights = []
            config = self.get_config()

            for saved_light in config:

                light = Light(saved_light["mac"], saved_light["ip"])

                menu_item = LightItem()
                menu_item.light = light
                menu_item.main_window = self

                try:
                    menu_item.light_label.set_text(light.get_label())
                    menu_item.light_switch.set_active(light.get_power() / 65535)
                except WorkflowException:
                    menu_item.set_sensitive(False)
                    menu_item.light_label.set_text(saved_light["label"])

                self.sidebar.insert(menu_item, -1)
                self.lights.append(light)

        self.refresh_stack.set_visible_child_name("refresh")

    @Gtk.Template.Callback("reload")
    def reload(self, sender):
        """
        Restart discovery or repopulate the sidebar.
        """

        if self.discovery_active:
            self.init_discovery()
        else:
            self.update_sidebar()

    @Gtk.Template.Callback("toggle_discovery")
    def toggle_discovery(self, sender):
        """
        Enables or disables discovery mode. Sets window title bar style etc.
        """

        self.clear_sidebar()
        self.active_light = None
        self.discovery_active = self.discovery_btn.get_active()

        self.title_bar.set_selection_mode(self.discovery_active)
        self.controls_box.set_visible(not self.discovery_active)

        self.content_stack.set_visible_child_name("empty")
        self.name_label.set_text("")
        self.ip_label.set_text("")

        self.content_box.set_visible_child(self.menu)

        if self.discovery_active:
            self.init_discovery()
            self.edit.set_sensitive(False)
        else:
            self.refresh_stack.set_visible_child_name("loading")
            self.refresh_spinner.start()

            self.update_sidebar()

    # Main light management

    @Gtk.Template.Callback("set_light_power")
    def set_light_power(self, sender, user_data):
        """
        Handler for power switch (only visible in folded state).
        """

        self.update_power(self.power_switch.get_active())

    def update_power(self, power):
        """
        Updates the bulbs power state and makes sure the power switches are in
        sync.
        """

        self.active_light.light.set_power(power, rapid=True)
        self.active_light.light_switch.set_active(power)
        self.power_switch.set_active(power)

    def update_light_state(self):
        """
        Probes the bulb for color information so it can be stored locally.
        """

        (hue, saturation, brightness, kelvin) = self.active_light.light.get_color()

        self.active_light.light.hue = decode_circle(hue)
        self.active_light.light.saturation = decode(saturation)
        self.active_light.light.brightness = decode(brightness)
        self.active_light.light.kelvin = kelvin

    def set_active_light(self):
        """
        Prepares the window for a change in active light. Updates color data etc.
        """

        if not self.sidebar.get_selected_row():
            return

        self.active_light = self.sidebar.get_selected_row()
        self.update_active = True

        if not self.discovery_active:
            self.edit.set_sensitive(True)

            self.update_light_state()

            self.power_switch.set_active(self.active_light.light.get_power() / 65535)
            self.hue_scale.set_value(self.active_light.light.hue)
            self.saturation_scale.set_value(self.active_light.light.saturation)
            self.brightness_scale.set_value(self.active_light.light.brightness)
            self.kelvin_scale.set_value(self.active_light.light.kelvin)

        self.name_label.set_text(self.active_light.light.get_label())
        self.ip_label.set_text(self.active_light.light.get_ip_addr())

        self.content_stack.set_visible_child_name("controls")
        self.content_box.set_visible_child(self.content_stack)

        self.header_box.set_visible_child(self.sub_header_bar)

        self.group_label.set_text(self.active_light.light.get_group_label())
        self.location_label.set_text(self.active_light.light.get_location_label())

        self.update_active = False

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

        if int(hue) == int(self.active_light.light.hue) and \
           int(saturation) == int(self.active_light.light.saturation) and \
           int(brightness) == int(self.active_light.light.brightness) and \
           int(kelvin) == int(self.active_light.light.kelvin):
               return

        self.active_light.light.set_color((encode_circle(hue),
                                           encode(saturation),
                                           encode(brightness),
                                           kelvin), rapid=True)

        self.active_light.light.hue = hue
        self.active_light.light.saturation = saturation
        self.active_light.light.brightness = brightness
        self.active_light.light.kelvin = kelvin

    # Editing label

    @Gtk.Template.Callback("name_changed")
    def name_changed(self, sender):
        """
        Checks to see if the edit toggle button should be disabled if the name
        is empty.
        """

        self.edit.set_sensitive(self.edit_label.get_text())

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
            self.edit_label.set_text(self.active_light.light_label.get_text())
            self.edit.set_active(False)

    @Gtk.Template.Callback("do_edit")
    def do_edit(self, sender):
        """
        Toggle edit label mode.
        """

        if not isinstance(self.active_light, LightItem):
            return

        if self.edit.get_active():
            self.edit_label.set_text(self.active_light.light_label.get_text())
            self.edit_stack.set_visible_child_name("editing")
        else:
            new_label = self.edit_label.get_text()

            self.edit_stack.set_visible_child_name("normal")

            self.active_light.light.set_label(new_label)
            self.active_light.light_label.set_label(new_label)
            self.name_label.set_text(new_label)

    # Discovery

    def init_discovery(self):
        """
        Initialize discovery thread. Starts spinner etc.
        """

        self.refresh_stack.set_visible_child_name("loading")
        self.refresh_spinner.start()

        discovery_thread = threading.Thread(target=self.discovery)
        discovery_thread.daemon = True
        discovery_thread.start()

    def discovery(self):
        """
        Discovery thread.
        """

        self.d_lights = self.lan.get_lights()
        GLib.idle_add(self.update_sidebar)

    def __init__(self, **kwargs):
        """
        Check if LifxLAN api available, small ui initialization.
        """

        super().__init__(**kwargs)

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

        self.lan = lifxlan.LifxLAN()

        self.edit.set_sensitive(False)
        self.content_stack.set_visible_child_name("empty")

        self.update_sidebar()
