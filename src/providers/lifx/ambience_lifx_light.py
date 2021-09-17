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

class AmbienceLIFXLight(AmbienceLight):
    """
    Bridge between lifxlan and ui.
    """
    
    def __init__(self, light_config, group):
        self.lifx_light = Light(light_config["mac"], light_config["ip"])
        self.label = light_config["label"]
        self.group = group

    def get_capabilities(self) -> list:
        capabilities = []

        if self.lifx_light.supports_color():
            capabilities.append(AmbienceLightCapabilities.COLOR)

        if self.lifx_light.supports_temperature():
            capabilities.append(AmbienceLightCapabilities.TEMPERATURE)

        if self.lifx_light.supports_multizone():
            capabilities.append(AmbienceLightCapabilities.MULTIZONE)

        if self.lifx_light.supports_infrared():
            capabilities.append(AmbienceLightCapabilities.INFRARED)

        return capabilities

    def get_online(self) -> bool:
        try:
            remote_label = self.lifx_light.get_label()
            if not remote_label == self.label: # Config remote mismatch
                self.lifx_light.label = remote_label
                # TODO: write config file

            return True
        except:
            return False

    def get_label(self) -> str:
        return self.lifx_light.label

    def set_label(self, label):
        self.lifx_light.set_label(label)

    def get_power(self) -> bool:
        return False if self.lifx_light.get_power() == 0 else True

    def set_power(self, power):
        self.lifx_light.set_power(power, rapid=True)

    def get_color(self) -> tuple[float, float, float, float]:
        color_hsvk = list(self.lifx_light.get_color())
        for i in range(3):
            color_hsvk[i] = color_hsvk[i] / 65535

        return tuple(color_hsvk)

    def set_color(self, hsvk):
        for i in range(3):
            hsvk[i] = hsvk[i] * 65535
        self.lifx_light.set_color(hsvk, rapid=True)

    def get_infrared(self) -> float:
        if AmbienceLightCapabilities.INFRARED in self.get_capabilities():
            return self.lifx_light.get_infrared() / 65535
        return 0

    def set_infrared(self, i):
        self.lifx_light.set_infrared(i * 65535)

    def get_info(self):
        return {AmbienceDeviceInfoType.IP       : self.lifx_light.get_ip_addr(),
                AmbienceDeviceInfoType.GROUP    : self.lifx_light.get_group(),
                AmbienceDeviceInfoType.LOCATION : self.lifx_light.get_location()
                }