# ambience_light_control.py
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

from gi.repository import Gtk, Gdk, GLib
from .helpers import *

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ambience_light_control.ui')
class AmbienceLightControl(Gtk.Box):
    __gtype_name__ = 'AmbienceLightControl'

    main_stack = Gtk.Template.Child()

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

    power_switch = Gtk.Template.Child()

    light_label = Gtk.Template.Child()
    light_sub_label = Gtk.Template.Child()

    light = None
    deck = None
    back_callback = None
    plist_downloader = None

    def __init__(self, light, deck, plist_downloader, back_callback, **kwargs):
        self.light = light
        self.deck = deck
        self.plist_downloader = plist_downloader
        self.back_callback = back_callback

        super().__init__(**kwargs)

    def show(self):
        self.update_active = True
        self.main_stack.set_visible_child_name("loading")

        def show_light_cb(_, success):
            if success:
                GLib.idle_add(self.update_controls)
            else:
                def display_error():
                    error_dialog = Gtk.MessageDialog(transient_for=self.get_toplevel(),
                                                    flags=0,
                                                    message_type=Gtk.MessageType.ERROR,
                                                    buttons=Gtk.ButtonsType.OK,
                                                    text="Unable to load light data. Please try again.",)
                    error_dialog.run()
                    self.back_callback(self)
                    error_dialog.destroy()

                GLib.idle_add(display_error)

        fetch_thread = threading.Thread(target=fetch_all_data, args=(self.light, show_light_cb))
        fetch_thread.daemon = True
        fetch_thread.start()

    def update_controls(self):
        self.light_label.set_text(self.light.label)

        if product_info := self.plist_downloader.get_product(self.light.product):
            self.light_sub_label.set_text(product_info["name"])

        self.power_switch.set_active(self.light.power)

        self.brightness_scale.set_value(self.light.brightness)

        if self.light.has_color:
            self.hue_row.set_visible(True)
            self.saturation_row.set_visible(True)

            self.hue_scale.set_value(self.light.hue)
            self.saturation_scale.set_value(self.light.saturation)

        if self.light.has_temp:
            self.kelvin_row.set_visible(True)
            self.kelvin_scale.set_value(self.light.temperature)

        if self.light.has_infrar:
            self.infrared_row.set_visible(True)
            self.infrared_scale.set_value(self.light.infrared)

        self.ip_label.set_label(self.light.ip)
        self.group_label.set_label(self.light.group)
        self.location_label.set_label(self.light.location)

        self.update_active = False
        self.main_stack.set_visible_child_name("controls")

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

        self.light.set_color((encode_circle(hue),
                                    encode(saturation),
                                    encode(brightness),
                                    kelvin), rapid=True)

        if self.light.supports_infrared():
            self.light.set_infrared(encode(self.infrared_scale.get_value()))

    @Gtk.Template.Callback("set_light_power")
    def set_light_power(self, sender, user_data):
        self.light.set_power(sender.get_active(), rapid=True)

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
            self.light_edit_label.set_text(self.light.label)
            self.edit.set_active(False)

    @Gtk.Template.Callback("do_edit")
    def do_edit(self, sender):
        """
        Toggle edit label mode.
        """
        if self.edit.get_active():
            self.light_edit_label.set_text(self.light.label)
            self.edit_stack.set_visible_child_name("editing")
        else:
            new_label = self.light_edit_label.get_text()

            self.edit_stack.set_visible_child_name("normal")

            self.light.set_label(new_label)
            self.light.label = new_label
            self.light_label.set_text(new_label)

    @Gtk.Template.Callback("go_back")
    def go_back(self, sender):
        self.back_callback(self)