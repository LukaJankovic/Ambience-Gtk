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

from .ambience_light import AmbienceLightCapabilities
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

    def __init__(self, light, deck, back_callback, **kwargs):
        self.light = light
        self.deck = deck
        self.back_callback = back_callback

        super().__init__(**kwargs)

    def show(self):

        (hue, saturation, brightness) = self.light.get_color()

        if AmbienceLightCapabilities.COLOR in self.light.get_capabilities():
            self.hue_row.set_visible(True)
            self.saturation_row.set_visible(True)

            self.hue_row.set_value(hue)
            self.saturation_row.set_value(saturation)

        if AmbienceLightCapabilities.TEMPERATURE in self.light.get_capabilties():
            self.kelvin_row.set_visible(True)
            self.kelvin_row.set_value()


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