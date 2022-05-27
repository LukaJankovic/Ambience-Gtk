# tile.py
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

from gi.repository import Gtk, Adw


@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/src/ui/tile.ui')
class AmbienceTile(Gtk.Button):
    """A widget that represents a device in the form of a tile."""

    __gtype_name__ = 'AmbienceTile'

    top_label = Gtk.Template.Child()
    bottom_label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
