from typing import Dict
from gi.repository import GLib, Gio
from lifxlan import *
import json

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
                return config

def add_light_to_group(config, label, light):
    group_index = -1
    for group in range(len(config["groups"])):
        if config["groups"][group]["label"] == label:
            group_index = group 
            break

    if group_index > -1:
        exists = False
        for light in config["groups"][group_index]["lights"]:
            if light["ip"] == light["ip"] and light["mac"] == light["mac"]:
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