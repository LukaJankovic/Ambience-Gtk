# ambience_settings.py
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

from typing import Dict
from gi.repository import GLib, Gio
import json

from .helpers import *

def get_old_dest_file():
    """
    Create / find the obsolete file used to store lights.
    """

    data_dir = GLib.get_user_config_dir()
    dest = GLib.build_filenamev([data_dir, "lights.json"])
    return Gio.File.new_for_path(dest)

def get_dest_file():
    """
    Create / find the file used to store lights.
    """

    data_dir = GLib.get_user_config_dir()
    dest = GLib.build_filenamev([data_dir, "ambience.json"])
    return Gio.File.new_for_path(dest)

def get_config(dest_file):
    """
    Loads the config file into a dictionary.
    """
    try:
        (success, content, tag) = dest_file.load_contents()
        return json.loads(content.decode("utf-8"))
    except GLib.GError as error:
        # File doesn't exist
        dest_file.create(Gio.FileCopyFlags.NONE, None)
    except (TypeError, ValueError) as e:
        # File is most likely empty
        print("Config file empty")
    return {"groups":[]}

def remove_light_from_group(config, mac):
    for group_idx in range(len(config["groups"])):
        for light in config["groups"][group_idx]["lights"]:
            if light["mac"] == mac:
                config["groups"][group_idx]["lights"].remove(light)
                break
        
        if len(config["groups"][group_idx]["lights"]) == 0:
            config["groups"].pop(group_idx)

        return config

def add_light_to_group(config, label, light):
    group_index = -1
    for group in range(len(config["groups"])):
        if config["groups"][group]["label"] == label:
            group_index = group 
            break

    if group_index > -1:
        exists = False
        for l in config["groups"][group_index]["lights"]:
            if l["ip"] == light["ip"] and l["mac"] == light["mac"]:
                exists = True
                break

        if not exists:
            config["groups"][group_index]["lights"].append(light)
    else:
        config["groups"].append({"label": label, "lights": [light]})
    return config

def write_config(config, dest_file):
    permissions = 0o664
    if GLib.mkdir_with_parents(dest_file.get_parent().get_path(), permissions) == 0:
        (success, _) = dest_file.replace_contents(str.encode(json.dumps(config)), None, False, Gio.FileCreateFlags.REPLACE_DESTINATION, None)

        if not success:
            print("Unable to save config file")
    else:
        print("Unable to create required directory/ies for config file")

def convert_old_config():
    print("Converting old config file...")

    old = get_config(get_old_dest_file())
    new = get_config(get_dest_file())

    for l in old:
        light = Light(l["mac"], l["ip"])

        try:
            group = light.get_group_label()
            new = add_light_to_group(new, group, l)
        except WorkflowException:
            in_new = False
            for group in new["groups"]:
                for light in group["lights"]:
                    if l["mac"] == light["mac"] and l["ip"] and light["ip"]:
                        in_new = True
                        break

            if not in_new:
                new = add_light_to_group(new, "Unknown Group", l)

    write_config(new, get_dest_file())

def move_old_config():
    data_dir = GLib.get_user_config_dir()
    dest = GLib.build_filenamev([data_dir, "lights.json.bak"])
    target = Gio.File.new_for_path(dest)
    get_old_dest_file().move(target, Gio.FileCopyFlags.NONE, None, None, None)