from typing import Dict
from gi.repository import GLib, Gio
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

def get_config():
    """
    Loads the config file into a dictionary.
    """

    dest_file = get_dest_file()

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
    if label in config["groups"]:
        config["groups"][label]["lights"].append(light)
    else:
        config["groups"].append({"label": label, "lights": [light]})
    return config