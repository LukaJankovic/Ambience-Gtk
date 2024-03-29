# ambience_lifx_group.py
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

from ambience.model.ambience_module_group import AmbienceModuleGroup

from lifxlan import Group

class AmbienceLIFXGroup(AmbienceModuleGroup):

    lights = None
    group = None

    def __init__(self, lights):
        self.lights = [light.lifx_light for light in lights]
        self.group = Group(self.lights)

    def set_color(self, hsvk):
        for i in range(3):
            hsvk[i] = hsvk[i] * 65535
        self.group.set_color(hsvk, rapid=True)
    
    def set_infrared(self, infrared):
        # INFRARED FOR GROUP NOT IMPLEMENTED
        pass

    def set_power(self, power):
        self.group.set_power(power, rapid=True)