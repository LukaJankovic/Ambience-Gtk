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

from ambience.providers.ambience_providers import AmbienceProviders

from lifxlan import Group

class AmbienceGroup():
    """
    Colleciton of AmbienceLights.
    """

    providers = AmbienceProviders()

    def __init__(self, group_config):
        self.label = group_config["label"]

        self.online = []
        self.offline = [] 

        for light_config in group_config["lights"]: # TODO: parallelize using joblib (maybe)
            module = light_config["kind"]
            connector = self.providers.import_provider(module)
            light = connector.create_device(light_config, self)
            self.providers.unimport_provider(connector) 

            if light.get_online():
                self.online.append(light)
            else:
                self.offline.append(light) 

    def get_lights_of_kind(self, connector):
        lights = [light for light in self.online if connector.compare_device(light)]
        return lights

    def set_color(self, hsvk):
        for kind in self.providers.get_provider_list():
            connector = self.providers.import_provider(kind)
            connector.create_group(self.get_lights_of_kind(connector)).set_color(hsvk) 

    def set_infrared(self, infrared):
        for kind in self.providers.get_provider_list():
            connector = self.providers.import_provider(kind)
            connector.create_group(self.get_lights_of_kind(connector)).set_infrared(infrared) 

    def set_power(self, power):
        for kind in self.providers.get_provider_list():
            connector = self.providers.import_provider(kind)
            connector.create_group(self.get_lights_of_kind(connector)).set_power(power) 