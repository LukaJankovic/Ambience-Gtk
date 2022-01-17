# ambience_module_connector.py
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

from gi.repository import Gtk
import json

from ambience.model.ambience_device import AmbienceDevice

class AmbienceModuleConnectorException(Exception):
    """
    Raised when a function call is made directly onto an AmbienceModuleConnector
    Object.
    """

class AmbienceModuleConnector():
    """
    Template class for connecting a module to Ambience. Every subclass must
    be named "AmbienceConnector" and be placed inside "ambience_connector.py"
    and overwrite all functions.
    """

    def display_name(self) -> str:
        raise AmbienceModuleConnectorException

    def compare_device(self, device) -> bool:
        raise AmbienceModuleConnectorException

    def save_device(self, device) -> dict:
        raise AmbienceModuleConnectorException

    def load_device(self, config, group) -> AmbienceDevice:
        raise AmbienceModuleConnector

    def create_group(self, devices):
        raise AmbienceModuleConnectorException

    def discovery_list(self) -> list[AmbienceDevice]:
        raise AmbienceModuleConnectorException 