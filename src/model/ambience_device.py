# ambience_device.py
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

from enum import Enum

class AmbienceDeviceException(Exception):
    """
    Raised when a function call is made directly onto an (illegal)
    AmbienceLight object.
    """
    pass

class AmbienceDeviceInfoType(Enum):
    MODEL       = 0
    IP          = 1
    GROUP       = 2
    LOCATION    = 3  

class AmbienceDevice():
    """
    Template class to be extended by other template classes that want to
    represent a unique kind of device. (i.e. light)
    """

    group = None
    kind = None

    def get_label(self) -> str:
        raise AmbienceDeviceException 

    def set_label(self, label):
        raise AmbienceDeviceException

    def get_online(self) -> bool:
        raise AmbienceDeviceException

    def get_power(self) -> bool:
        raise AmbienceDeviceException

    def set_power(self, power):
        raise AmbienceDeviceException

    def get_info(self) -> dict:
        raise AmbienceDeviceException

    def write_config(self) -> dict:
        raise AmbienceDeviceException
