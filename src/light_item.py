# light_item.py
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

from gi.repository import Gtk, GLib, GObject

try:
    from lifxlan import *
except ImportError:
    pass

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ui/light_item.ui')
class LightItem(Gtk.ListBoxRow):
    """
    Sidebar item containing the name of the bulb as well as a power switch.
    """

    __gtype_name__ = 'LightItem'

    light_label  = Gtk.Template.Child()
    light_switch = Gtk.Template.Child()

    light = None
    main_window = None

    @Gtk.Template.Callback("activate_switch")
    def activate_switch(self, sender, user_data):
        """
        Power switch toggled. Run command in main window if I'm the current
        bulb to retain sync with switch in the main window.
        """

        if isinstance(self.light, Device):
            power = self.light_switch.get_active()
            if self.main_window.active_light == self:
                self.main_window.update_power(power)
            else:
                self.light.set_power(power)
