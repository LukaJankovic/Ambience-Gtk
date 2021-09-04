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

class AmbienceDeviceException(Exception):
    """
    Raised when a function call is made directly onto an (illegal)
    AmbienceLight object.
    """
    pass

class AmbienceDevice():
    """
    Template class to be extended by other template classes that want to
    represent a unique kind of device. (i.e. light)
    """

    def get_label(self) -> str:
        raise AmbienceDeviceException 

    def get_online(self) -> bool:
        raise AmbienceDeviceException