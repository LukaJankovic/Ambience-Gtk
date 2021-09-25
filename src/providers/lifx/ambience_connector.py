# ambience_lifx_connector.py
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

from ambience.module.ambience_module_group_connector import AmbienceModuleGroupConnector

from .ambience_lifx_light import AmbienceLIFXLight
from .ambience_lifx_group import AmbienceLIFXGroup

class AmbienceConnector(AmbienceModuleGroupConnector):
    def display_name(self):
        return "LIFX"

    def create_device(self, config, group):
        return AmbienceLIFXLight(config, group)

    def compare_device(self, device):
        return isinstance(device, AmbienceLIFXLight)

    def create_group(self, devices):
        return AmbienceLIFXGroup(devices)