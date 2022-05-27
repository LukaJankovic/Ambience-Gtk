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

import json, pprint

class JSONObject():
    """Convenience-class used to convert JSON into Python object.
    
    Credit: https://stackoverflow.com/a/54640137
    """
    
    changed_cb = None
    
    @classmethod
    def from_dict(cls, dict):
        obj = cls()
        obj.__dict__.update(dict)
        return obj
    
    def __setattr__(self, name, value):
        """Calls a callback function whenever an attribute is changed."""
        if self.changed_cb:
            self.changed_cb()
        super(JSONObject, self).__setattr__(name, value)

class Provider():
    """Exposes an interface for the UI to access lights from different 
    providers.
    """
    
    config = None
    
    def __init__(self, path):
        """Reads config file from user and returns it in form of a dict.
        
        Args:
            path: path to the config file to be read
        """
        
        # Open config file
        data_dir = GLib.get_user_config_dir()
        dest = GLib.build_filenamev([data_dir, path])
        file = Gio.File.new_for_path(dest)
        
        # (Attempt to) read and parse config file
        try:
            (success, content, _) = file.load_contents()
            self.config = json.loads(content.decode('utf-8'),
                                     object_hook=JSONObject.from_dict)
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
        if not self.config:
            self.config = json.loads('{"version": "1.4", "groups": []}',
                                     object_hook=JSONObject.from_dict)
        
        self.config.changed_cb = self.config_changed_cb
        
    def config_changed_cb(self):
        """Called whenever the config object changed."""
        print("config updated")
