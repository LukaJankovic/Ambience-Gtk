# ambience_lifx_lan.py
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

from ambience.singleton import *

try:
    from lifxlan import *
    API_AVAIL = True
except:
    API_AVAIL = False

class AmbienceLIFXLan(metaclass=Singleton):
    """
    Singleton class containing a shared LifxLAN object.
    """

    lan = None

    def check_api_availability(self):
        return API_AVAIL

    def get_lan(self):
        if not self.lan:
            self.lan = LifxLAN()
        return self.lan
