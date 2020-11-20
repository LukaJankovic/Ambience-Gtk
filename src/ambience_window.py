# window.py
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

from gi.repository import Gtk, GLib, GObject, Handy
from lifxlan import *
from .light_item import *
from .discovery_item import *
import json

@Gtk.Template(resource_path='/org/lukjan/ambience/ui/ambience_window.ui')
class AmbienceWindow(Handy.ApplicationWindow):
    __gtype_name__ = 'AmbienceWindow'

    main_popover    = Gtk.Template.Child()

    title_bar       = Gtk.Template.Child()
    header_box      = Gtk.Template.Child()
    content_box     = Gtk.Template.Child()

    menu            = Gtk.Template.Child()
    header_bar      = Gtk.Template.Child()
    refresh_stack   = Gtk.Template.Child()
    refresh         = Gtk.Template.Child()
    refresh_spinner = Gtk.Template.Child()
    discovery_btn   = Gtk.Template.Child()
    sidebar         = Gtk.Template.Child()

    content_stack   = Gtk.Template.Child()
    sub_header_bar  = Gtk.Template.Child()
    edit_stack      = Gtk.Template.Child()
    back            = Gtk.Template.Child()
    edit            = Gtk.Template.Child()
    edit_label      = Gtk.Template.Child()
    name_label      = Gtk.Template.Child()
    ip_label        = Gtk.Template.Child()

    power_row       = Gtk.Template.Child()
    power_switch    = Gtk.Template.Child()
    hue_scale       = Gtk.Template.Child()
    saturation_scale= Gtk.Template.Child()
    brightness_scale= Gtk.Template.Child()
    kelvin_scale    = Gtk.Template.Child()

    group_label     = Gtk.Template.Child()
    location_label  = Gtk.Template.Child()

    lan    = LifxLAN()
    lights = []
    d_lights = []

    active_light = None
    discovery_active = False

    # Misc. File Management

    def get_dest_file(self):
        data_dir = GLib.get_user_config_dir()
        dest = GLib.build_filenamev([data_dir, "lights.json"])
        return Gio.File.new_for_path(dest)

    def get_config(self):
        dest_file = self.get_dest_file()

        try:
            (success, content, tag) = dest_file.load_contents()
            return json.loads(content.decode("utf-8"))
        except GLib.GError as error:
            # File doesn't exist
            dest_file.create(Gio.FileCopyFlags.NONE, None)
        except (TypeError, ValueError) as e:
            # File is most likely empty
            print("invalid JSON")
            print(str(e))
        return []

    # Misc. Window / UI Management

    @Gtk.Template.Callback("notify_fold_cb")
    def notify_fold_cb(self, sender, user_data):

        folded = self.content_box.get_folded()

        if folded:
            self.back.show_all()
            self.power_row.show_all()

            if isinstance(self.active_light, LightItem):
                self.power_switch.set_active(self.active_light.light_switch.get_active())

            self.sidebar.unselect_all()
        else:
            self.back.hide()
            self.power_row.hide()

            self.sidebar.select_row(self.active_light)

        self.header_bar.set_show_close_button(folded)

    def go_back(self, sender):
        self.active_light = None
        self.sidebar.unselect_all()
        self.content_box.set_visible_child(self.menu)
        self.header_box.set_visible_child(self.header_bar)

    def sidebar_selected(self, sender, user_data):
        self.set_active_light()

    def clear_sidebar(self):
        for sidebar_item in self.sidebar.get_children():
            self.sidebar.remove(sidebar_item)

    # Reloading

    def update_sidebar(self):

        self.clear_sidebar()

        if self.discovery_active:
            config_list = self.get_config()

            for light in self.d_lights:
                sidebar_item = DiscoveryItem()
                sidebar_item.light = light
                sidebar_item.light_label.set_text(light.get_label())
                sidebar_item.dest_file = self.get_dest_file()
                sidebar_item.config_list = config_list

                for l in config_list:
                    if l["mac"] == light.get_mac_addr():
                        sidebar_item.added = True
                        sidebar_item.update_icon()
                        break

                self.sidebar.insert(sidebar_item, -1)

        else:
            self.lights = []
            config = self.get_config()

            for light in config:

                l = Light(light["mac"], light["ip"])

                sidebar_item = LightItem()
                sidebar_item.light = l

                try:
                    sidebar_item.light_label.set_text(l.get_label())
                    sidebar_item.light_switch.set_active(l.get_power() / 65535)
                except WorkflowException:
                    sidebar_item.set_sensitive(False)
                    sidebar_item.light_label.set_text(light["label"])

                self.sidebar.insert(sidebar_item, -1)
                self.lights.append(l)

        self.refresh_stack.set_visible_child_name("refresh")

    def reload(self, sender):
        if self.discovery_active:
            self.init_discovery()
        else:
            self.update_sidebar()

    def toggle_discovery(self, sender):
        self.clear_sidebar()
        self.discovery_active = self.discovery_btn.get_active()

        self.title_bar.set_selection_mode(self.discovery_active)
        self.edit.set_sensitive(not self.discovery_active)

        if self.discovery_active:
            self.init_discovery()
        else:
            self.refresh_stack.set_visible_child_name("loading")
            self.refresh_spinner.start()

            self.update_sidebar()

    # Main light management

    @Gtk.Template.Callback("set_light_power")
    def set_light_power(self, sender, user_data):

        power = self.power_switch.get_active()

        self.active_light.light.set_power(power)
        self.active_light.light_switch.set_active(power)

    def set_active_light(self):

        self.active_light = self.sidebar.get_selected_row()

        self.name_label.set_text(self.active_light.light.get_label())
        self.ip_label.set_text(self.active_light.light.get_ip_addr())

        (hue, saturation, brightness, kelvin) = self.active_light.light.get_color()

        self.power_switch.set_active(self.active_light.light.get_power() / 65535)
        self.hue_scale.set_value((hue / 65535) * 360)
        self.saturation_scale.set_value((saturation / 65535) * 100)
        self.brightness_scale.set_value((brightness / 65535) * 100)
        self.kelvin_scale.set_value(kelvin)

        self.content_stack.set_visible_child_name("controls")
        self.content_box.set_visible_child(self.content_stack)

        self.header_box.set_visible_child(self.sub_header_bar)

        self.group_label.set_text(self.active_light.light.get_group_label())
        self.location_label.set_text(self.active_light.light.get_location_label())

    def push_color(self, sender):

        hue         = (self.hue_scale.get_value() / 360) * 65535
        saturation  = (self.saturation_scale.get_value() / 100) * 65535
        brightness  = (self.brightness_scale.get_value() / 100) * 65535
        kelvin      = self.kelvin_scale.get_value()

        self.active_light.light.set_color((hue, saturation, brightness, kelvin), rapid=True)

    # Editing

    def do_edit(self, sender):
        if not isinstance(self.active_light, LightItem):
            return

        if self.edit.get_active():
            self.edit_label.set_text(self.active_light.light_label.get_text())
            self.edit_stack.set_visible_child_name("editing")
        else:
            self.edit_stack.set_visible_child_name("normal")

            new_label = self.edit_label.get_text()

            self.active_light.light.set_label(new_label)
            self.active_light.light_label.set_label(new_label)
            self.name_label.set_text(new_label)

    # Discovery

    def init_discovery(self):

        self.content_stack.set_visible_child_name("empty")
        self.name_label.set_text("")
        self.ip_label.set_text("")

        self.refresh_stack.set_visible_child_name("loading")
        self.refresh_spinner.start()

        discovery_thread = threading.Thread(target=self.discovery)
        discovery_thread.daemon = True
        discovery_thread.start()

    def discovery(self):
        self.d_lights = self.lan.get_lights()
        GLib.idle_add(self.update_sidebar)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.back.connect("clicked", self.go_back)
        self.refresh.connect("clicked", self.reload)
        self.discovery_btn.connect("clicked", self.toggle_discovery)
        self.sidebar.connect("row-selected", self.sidebar_selected)

        self.hue_scale.connect("value-changed", self.push_color)
        self.saturation_scale.connect("value-changed", self.push_color)
        self.brightness_scale.connect("value-changed", self.push_color)
        self.kelvin_scale.connect("value-changed", self.push_color)

        self.edit.connect("clicked", self.do_edit)
        self.content_stack.set_visible_child_name("empty")

        self.update_sidebar()
