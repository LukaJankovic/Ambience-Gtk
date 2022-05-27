# window.py
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

from .tile import AmbienceTile
from .row import AmbienceRow

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/src/ui/window.ui')
class AmbienceWindow(Adw.ApplicationWindow):
    """The main application window class.

    Responsible for populating group list as well as view switching
    """

    __gtype_name__ = 'AmbienceWindow'

    content_box     = Gtk.Template.Child()
    light_tile_list = Gtk.Template.Child()
    main_flap       = Gtk.Template.Child()
    sidebar         = Gtk.Template.Child()
    
    provider = None

    def __init__(self, provider, **kwargs):
        super().__init__(**kwargs)

        self.provider = provider

        self.populate_sidebar(self.provider.config.groups)

    @Gtk.Template.Callback("sidebar_row_selected_cb")
    def sidebar_row_selected_cb(self, sender, user_data):
        """Row selected in sidebar callback.

        Hides the flap if it was opened and a new group was selected.
        Args:
            sender:     which object caused the callback to be triggered
            user_data:  optional user data (not used)
        """
        if self.main_flap.get_folded():
            self.main_flap.set_reveal_flap(False)

        selected = sender.get_selected_row()

        self.populate_from_group(self.provider.config.groups,
                                 selected.get_index())

        # End editing for all rows
        row = sender.get_first_child()
        row.end_edit()
        while row := row.get_next_sibling():
            row.end_edit()

    def populate_from_group(self, groups, idx):
        """Populates main content.

        Args:
            groups: dict containing all groups and devices
            ixd:    index of the group to populate data from
        """
        self.clear_tiles()
        for device in groups[idx].devices:
            tile = AmbienceTile()
            tile.top_label.set_label(device.label)

            self.light_tile_list.insert(tile, -1)

    def populate_sidebar(self, groups):
        """Populates sidebar list with groups.

        Args:
            groups: dict containing all groups and devices
        """
        self.clear_sidebar()

        for group in groups:
            row = AmbienceRow(group)
            self.sidebar.insert(row, -1)

    def clear_tiles(self):
        """Removes all tiles from tiles box."""

        while tile := self.light_tile_list.get_first_child():
            self.light_tile_list.remove(tile)

    def clear_sidebar(self):
        """Removes all entries from the sidebar."""

        while entry := self.sidebar.get_first_child():
            self.sidebar.remove(entry)
