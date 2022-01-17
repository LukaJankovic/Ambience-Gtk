# ambience_group_control.py
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

from gi.repository import Gtk

from ambience.model.ambience_light import AmbienceLightCapabilities

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ambience_group_control.ui')
class AmbienceGroupControl(Gtk.Box):
    __gtype_name__ = 'AmbienceGroupControl'

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

    power_switch = Gtk.Template.Child()

    light_label = Gtk.Template.Child()
    light_sub_label = Gtk.Template.Child()

    group = None
    deck = None
    back_callback = None
    capabilities = []
    has_infrared = False

    def __init__(self, group, deck, back_callback, online, **kwargs):
        self.group = group
        self.online = online # TODO: Update online devices
        self.deck = deck
        self.back_callback = back_callback

        super().__init__(**kwargs)

    def show(self):
        self.update_active = True

        self.light_label.set_label(self.group.label)

        if len(self.online) == 1:
            self.light_sub_label.set_label("One light online")
        else:
            self.light_sub_label.set_label(str(len(self.online)) + " lights online")

        self.update_controls()
    
    def get_capabilities(self):
        self.capabilities = [c.value for c in AmbienceLightCapabilities]
        for light in self.online:
            for c in self.capabilities:
                if not c in light.get_capabilities():
                    self.capabilities.remove(c)

    def update_controls(self):
        self.update_active = True

        if power := self.get_group_value(AmbienceLightCapabilities.POWER):
            self.power_switch.set_active(power)

        (hue, saturation, brightness, kelvin) = self.get_group_value(AmbienceLightCapabilities.COLOR)

        if brightness:
            self.brightness_scale.set_value(brightness * 100)

        if hue:
            self.hue_scale.set_value(hue * 365)

        if saturation: 
            self.saturation_scale.set_value(saturation * 100)

        if kelvin:
            self.kelvin_scale.set_value(kelvin)

        if infrared := self.get_group_value(AmbienceLightCapabilities.INFRARED):
            self.infrared_scale.set_value(infrared * 100)

        self.update_active = False 

    def get_group_value(self, capability):
        value = -1
        for light in self.online:
            if value == -1:
                value = light.get_data(capability)
            elif not value == light.get_data(capability):
                break

        if value == -1:
            return None
        return value

    @Gtk.Template.Callback("push_color")
    def push_color(self, sender):
        if self.update_active:
            return

        hue = self.hue_scale.get_value()
        saturation = self.saturation_scale.get_value()
        brightness = self.brightness_scale.get_value()
        kelvin = self.kelvin_scale.get_value()
        infrared = self.infrared_scale.get_value()

        self.group.set_color([hue / 365, saturation / 100, brightness / 100, kelvin])
        self.group.set_infrared(infrared / 100)

    @Gtk.Template.Callback("set_light_power")
    def set_light_power(self, sender, user_data):
        if self.update_active:
            return

        self.group.set_power(self.power_switch.get_active())

    @Gtk.Template.Callback("go_back")
    def go_back(self, sender):
        self.back_callback(self)