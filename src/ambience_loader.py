# ambience_loader.py
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

from gi.repository import GLib, Gio

from ambience.model.ambience_group import *
from ambience.singleton import *

import json

class AmbienceLoader(metaclass=Singleton):
    """
    Loads config file, checks which lights are online and creates lists containing
    AmbienceLight descended objects.
    """

    CONFIG_FILE_NAME = 'ambience.json'

    def read_config_file(self, file):
        data_dir = GLib.get_user_config_dir()
        dest = GLib.build_filenamev([data_dir, file])
        return Gio.File.new_for_path(dest)

    def get_config(self):
        file = self.read_config_file(self.CONFIG_FILE_NAME)
        try:
            (_, content, _) = file.load_contents()
            return json.loads(content.decode("utf-8"))
        except GLib.GError as error:
            # File doesn't exist
            file.create(Gio.FileCopyFlags.NONE, None)
        except (TypeError, ValueError) as e:
            # File is most likely empty
            print("Config file empty or invalid")
        return {"groups":[]}

    def write_config(self, config):
        permissions = 0o664
        target_file = self.read_config_file(self.CONFIG_FILE_NAME)
        if GLib.mkdir_with_parents(target_file.get_parent().get_path(), permissions) == 0:
            (success, _) = target_file.replace_contents(str.encode(json.dumps(config)), None, False, Gio.FileCreateFlags.REPLACE_DESTINATION, None)

            if not success:
                print("Unable to save config file")
        else:
            print("Unable to create required directory/ies for config file")

    def get_group(self, label):
        config = self.get_config()

        for group in config["groups"]:
            if group["label"] == label:
                return AmbienceGroup.from_config(group)

        group = AmbienceGroup()
        group.label = label

        config["groups"].append(group.write_config())

        self.write_config(config)
        return group
    
    def remove_group(self, config, group):
        for g in config["groups"]:
            if g["label"] == group.get_label():
                config["groups"].remove(g)
        return config

    def get_all_groups(self):
        return [AmbienceGroup.from_config(x) for x in self.get_config()["groups"]]

    def has_device(self, device):
        config = self.get_config()

        for group in config["groups"]:
            for d in group["devices"]:
                if device.write_config() == d["data"]:
                    return True
        return False

    def modify_group(self, group, modify_fn):
        config = self.remove_group(self.get_config(), group)
        modify_fn()
        print(group.devices)
        config["groups"].append(group.write_config())
        self.write_config(config)

    def add_device(self, group, device):
        def add_fn():
            group.add_device(device)
        self.modify_group(group, add_fn)
        device.set_group(group)

    def remove_device(self, device, group=None):
        if not group:
            group = device.get_group()
        def rm_fn():
            group.remove_device(device)
        self.modify_group(group, rm_fn)
