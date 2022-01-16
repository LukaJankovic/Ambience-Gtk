# ambience_group.py
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

from ambience.providers.ambience_providers import AmbienceProviders

from lifxlan import Group, group

class AmbienceGroup():
    """
    Colleciton of AmbienceLights.
    """

    label = ""
    devices = []
    providers = AmbienceProviders()

    @classmethod
    def from_config(cls, group_config):
        new = cls()
        new.label = group_config["label"]

        new.devices = []

        for device_config in group_config["devices"]: # TODO: parallelize using joblib (maybe)
            module = device_config["kind"]
            connector = new.providers.import_provider(module)
            device = connector.load_device(device_config, new)
            device.set_group(new)
            new.devices.append(device)

        return new

    def write_config(self):
        config = {
            "label": self.label,
            "devices": []
        }

        for device in self.devices:
            device_config = {
                "label": device.get_label(),
                "kind": device.kind,
                "data": device.write_config()
            }
            config["devices"].append(device_config)

        return config

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

    def add_device(self, device):
        self.devices.append(device)

    def remove_device(self, device):
        if device in self.devices:
            self.devices.remove(device)
            return

        for d in self.devices:
            if d.write_config() == device.write_config():
                self.devices.remove(d)
                return

    def get_devices(self):
        return self.devices

    def has_device(self, device):
        for d in self.devices:
            if d.write_config() == device.write_config():
                return True
        
        return False

    def set_label(self, label):
        self.label = label

    def get_label(self):
        return self.label
