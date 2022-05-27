# connector.py
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

from gi.repository import GLib, Gio

import json

def to_dict(obj, classkey=None):
    """Converts any Python-object into dict.

    Taken from SO: https://stackoverflow.com/a/1118038

    Args:
        obj: object to be converted into dict
    """

    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = to_dict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return to_dict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [to_dict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, to_dict(value, classkey))
            for key, value in obj.__dict__.items()
            if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj

class JSONObject():
    """Convenience-class used to convert JSON into Python object and back.
    
    Credit / Inspiration:
        https://stackoverflow.com/a/54640137
        https://stackoverflow.com/a/1118038
    """
    
    changed_cb = None
    
    def __setattr__(self, name, value):
        """Calls a callback function whenever an attribute is changed."""
        super(JSONObject, self).__setattr__(name, value)

        if self.changed_cb:
            self.changed_cb()

class Provider():
    """Exposes an interface for the UI to access lights from different 
    providers.
    """
    
    config  = None
    path    = ""
    loading = False
    
    def __init__(self, path):
        self.path = path
        self.config = self.read_config(path)

    def read_config(self, path):
        """Reads config file from user and returns it in form of a dict.
        
        Args:
            path: path to the config file to be read
        """
        
        loading = True # Flag to not trigger __setattr__ while populating
        file = self.open_file(path)

        # (Attempt to) read and parse config file
        try:
            (success, content, _) = file.load_contents()
            config = json.loads(content.decode('utf-8'),
                                object_hook=self.create_JSONObject)
            # TODO: validate config
            
        except GLib.GError as error:
            # No config file exists, so we create one
            file.create(Gio.FileCopyFlags.NONE, None)
        except json.decoder.JSONDecodeError as e:
            # Error parsing json
            print("Unable to parse JSON", e)
        except (TypeError, ValueError) as e:
            # File exists but is probably empty or incorrect
            print("Unable to read config contents", e)
        
        # If reading config file failed, use empty config
        if not config:
            config = json.loads('{"version": "1.4", "groups": []}',
                                object_hook=self.create_JSONObject)

        loading = False

        return config

    def write_config(self, config, path):
        """Writes config to file.
        
        Args:
            config: config to be written to file
            path:   path of file to save config to
        """

        permissions = 0o664
        target = self.open_file(path)
        target_dir = target.get_parent().get_path()
        
        if GLib.mkdir_with_parents(target_dir, permissions) == 0:
            res = str.encode(json.dumps(to_dict(config)))
            flags = Gio.FileCreateFlags.REPLACE_DESTINATION
            (s, err) = target.replace_contents(res, None, False, flags, None)

            if not s:
                print("Unable to save config file", err)
        else:
            print("Unable to create required directory/ies for config file")

    def open_file(self, path):
        """Opens a file in user config for reading / writing.

        Args:
            path: path of file to be opened
        """

        data_dir = GLib.get_user_config_dir()
        dest = GLib.build_filenamev([data_dir, path])
        return Gio.File.new_for_path(dest)

    def create_JSONObject(self, data_dict):
        """Creates a JSONObject from dict and sets changed callback."""

        res = JSONObject()
        res.__dict__.update(data_dict)
        res.changed_cb = self.config_changed_cb
        return res

    def config_changed_cb(self):
        """Called whenever the config object changed."""

        if not self.loading:
            self.write_config(self.config, self.path)
