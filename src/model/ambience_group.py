# ambience_group.py
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

from .ambience_lifx_light import AmbienceLIFXLight
from lifxlan import Group

class AmbienceGroup():
    """
    Colleciton of AmbienceLights.
    """

    def __init__(self, group_config):
        self.label = group_config["label"]

        self.online = []
        self.offline = [] 

        for light_config in group_config["lights"]: # TODO: parallelize using joblib
            light = None
            if light_config["kind"] == "lifx":
                light = AmbienceLIFXLight(light_config, self)
                light.get_capabilities()
            else:
                continue

            if light.get_online():
                self.online.append(light)
            else:
                self.offline.append(light) 

    def get_lifx_lights(self):
        return [light.lifx_light for light in self.online if isinstance(light, AmbienceLIFXLight)]

    def set_color(self, hsvk):
        for i in range(3):
            hsvk[i] = hsvk[i] * 65535
        Group(self.get_lifx_lights()).set_color(hsvk)

    def set_infrared(self, infrared):
        Group(self.get_lifx_lights()).set_infrared(infrared)

    def set_power(self, power):
        Group(self.get_lifx_lights()).set_power(power)