# ambience_lifx_device_type.py
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

import requests, json

from .helpers import *

P_LIST_URL = "https://raw.githubusercontent.com/LIFX/products/master/products.json"

class AmbienceLifxDeviceType(metaclass=Singleton):
    """
    Class that attempts to download as well as manage the product list from 
    Lifx's official Github.
    """
    p_list = []

    def download_list(self) -> bool:
        """
        Downloads and saves the product list. Returns if successful.
        """
        if self.p_list:
            return

        resp = requests.get(P_LIST_URL)
        if resp.status_code == 200:
            self.p_list = json.loads(resp.content)[0]["products"]
            return True
        return False

    def get_product(self, pid) -> str:
        """
        Gets the product name based on id, otherwise returns None
        """
        if self.download_list():
            return next((l for l in self.p_list if l["pid"] == pid), None)
        return None