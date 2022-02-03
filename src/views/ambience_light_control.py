# ambience_light_control.py
#
# Copyright 2022 Luka Jankovic
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

from gi.repository import Gtk, Gdk, GLib
import threading

from ambience.model.ambience_light import AmbienceLightCapabilities
from ambience.model.ambience_device import AmbienceDeviceInfoType

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

    model_row = Gtk.Template.Child()
    model_label = Gtk.Template.Child()

    ip_row = Gtk.Template.Child()
    ip_label = Gtk.Template.Child()

    group_row = Gtk.Template.Child()
    group_label = Gtk.Template.Child()

    location_row = Gtk.Template.Child()
    location_label = Gtk.Template.Child()

    edit = Gtk.Template.Child()
    edit_stack = Gtk.Template.Child()
    light_edit_label = Gtk.Template.Child()

    power_switch = Gtk.Template.Child()

    light_label = Gtk.Template.Child()

    light = None
    deck = None
    back_callback = None
    update_active = False

    value_changed_cb = None

    def __init__(self, light, deck, back_callback, value_changed_cb, **kwargs):
        self.light = light
        self.deck = deck
        self.back_callback = back_callback
        self.value_changed_cb = value_changed_cb

        super().__init__(**kwargs)

    def show(self):
        """
        The view is ready to show. Update rows.
        """
        def show_async():

            #self.main_stack.set_visible_child_name("loading")

            for _ in range(5):
                try:
                    #self.label = self.light.get_label()
                    #self.power = self.light.get_power()

                    #self.color = self.light.get_color()

                    #self.capabilities = self.light.get_capabilities()

                    #if AmbienceLightCapabilities.INFRARED in self.capabilities:
                    #    self.infrared = self.light.get_infrared()

                    self.label = self.light.label
                    self.power = self.light.power
                    self.color = self.light.color
                    self.info = self.light.info
                    self.capabilities = self.light.capabilities

                    if AmbienceLightCapabilities.INFRARED in self.capabilities:
                        self.infrared = self.light.get_inrfared()
                    break

                except:
                    pass

            GLib.idle_add(self.update_rows)

        show_thread = threading.Thread(target=show_async)
        show_thread.daemon = True
        show_thread.start()

    def update_rows(self):
        self.main_stack.set_visible_child_name("controls")

        self.update_active = True

        self.light_label.set_label(self.label)
        self.power_switch.set_active(self.power)

        (hue, saturation, brightness, kelvin) = self.color

        self.brightness_scale.set_value(brightness * 100)

        if AmbienceLightCapabilities.COLOR in self.capabilities: 
            self.hue_row.set_visible(True)
            self.saturation_row.set_visible(True)

            self.hue_scale.set_value(hue * 365)
            self.saturation_scale.set_value(saturation * 100)

        if AmbienceLightCapabilities.TEMPERATURE in self.capabilities:
            self.kelvin_row.set_visible(True)
            self.kelvin_scale.set_value(kelvin)

        if AmbienceLightCapabilities.INFRARED in self.capabilities:
            self.infrared_row.set_visible(True)

        self.update_active = False

        rows = {
            AmbienceDeviceInfoType.MODEL    : self.model_row,
            AmbienceDeviceInfoType.IP       : self.ip_row,
            AmbienceDeviceInfoType.GROUP    : self.group_row,
            AmbienceDeviceInfoType.LOCATION : self.location_row
        }

        labels = {
            AmbienceDeviceInfoType.MODEL    : self.model_label,
            AmbienceDeviceInfoType.IP       : self.ip_label,
            AmbienceDeviceInfoType.GROUP    : self.group_label,
            AmbienceDeviceInfoType.LOCATION : self.location_label
        }

        for type in AmbienceDeviceInfoType:
            if type in self.info.keys():
                rows[type].set_visible(True)
                labels[type].set_text(self.info[type])
 
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

        hsbk = [hue / 365, saturation / 100, brightness / 100, kelvin]
        self.light.set_color(hsbk)
        self.light.color = hsbk

        if AmbienceLightCapabilities.INFRARED in self.light.capabilities:
            self.light.set_infrared(self.infrared_scale.get_value() * 100)

        self.value_changed_cb(self.light)

    @Gtk.Template.Callback("set_light_power")
    def set_light_power(self, sender, user_data):
        if self.update_active:
            return 

        power = sender.get_active()
        self.light.set_power(power)
        self.light.power = power

        self.value_changed_cb(self.light)

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

        if self.light_edit_label.get_text() and self.edit.get_active():
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

            self.value_changed_cb(self.light)

    @Gtk.Template.Callback("go_back")
    def go_back(self, sender):
        self.back_callback(self)