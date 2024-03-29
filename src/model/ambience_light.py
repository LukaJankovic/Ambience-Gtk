# ambience_light.py
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

from enum import Enum
from .ambience_device import *

class AmbienceLightException(Exception):
    """
    Raised when a function call is made directly onto an (illegal)
    AmbienceLight object.
    """
    pass

class AmbienceLightCapabilities(Enum):
    COLOR       = 1
    TEMPERATURE = 2
    MULTIZONE   = 3
    INFRARED    = 4
    POWER       = 5

class AmbienceLight(AmbienceDevice):
    """
    Template class extended by different providers to bind actions to ui.
    """
    label           = None
    available       = None
    capabilities    = None
    color           = None
    infrared        = None
    power           = None
    info            = None

    def get_capabilities(self) -> list:
        raise AmbienceLightException

    def get_color(self):
        raise AmbienceLightException 
    
    def set_color(self, hsvk):
        raise AmbienceLightException

    def get_infrared(self):
        raise AmbienceLightException

    def set_infrared(self, i):
        raise AmbienceLightCapabilities

    def get_data(self, capability):
        if capability == AmbienceLightCapabilities.COLOR:
            if self.color:
                return self.color
            return -1
        if capability == AmbienceLightCapabilities.TEMPERATURE:
            if self.temperature:
                return self.temperature
            return -1
        if capability == AmbienceLightCapabilities.INFRARED:
            if self.infrared:
                return self.infrared
            return -1
        if capability == AmbienceLightCapabilities.POWER:
            if self.power:
                return self.power
            return -1
