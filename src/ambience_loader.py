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
from .singleton import *

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

    def get_group_labels(self):
        config = self.get_config()
        groups = []

        for group in config["groups"]:
            groups.append(group["label"])

        return groups

    def get_group(self, label):
        config = self.get_config()

        for group in config["groups"]:
            if group["label"] == label:
                return AmbienceGroup(group)

    def add_light(self, group, ip, mac, kind):
        config = self.get_config()

        light = {
            "kind": kind,
            "ip":   ip,
            "mac":  mac
        }

        added = False
        for group in config["groups"]:
            if group["label"] == group.label:
                if "lights" in group:
                    group["lights"].append(light)
                else:
                    group["lights"] = [light]
                added = True

        if not added:
            config["groups"].append({
                "label": group.label,
                "lights": [light]
            })