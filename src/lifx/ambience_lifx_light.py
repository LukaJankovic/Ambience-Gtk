# ambience_lifx_light.py
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

from lifxlan import *
from .ambience_light import *
import colorsys

class AmbienceLIFXLight(AmbienceLight):
    """
    Bridge between lifxlan and ui.
    """
    
    def __init__(self, light_config):
        self.light.label = light_config["label"]
        self.light = Light(light_config[""])

    def get_label(self) -> str:
        return self.light.label

    def get_has_color(self) -> bool:
        return self.light.has_color

    def get_color(self) -> Tuple[float, float, float]:
        return colorsys.hsv_to_rgb(self.light.hue / 365,
                                   self.light.saturation / 100,
                                   self.light.brightness / 100)
        