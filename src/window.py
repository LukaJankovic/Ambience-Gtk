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

    test_data = {
        "group 1": ["thing 1", "really long long thing", "wow"],
        "another group": ["just one"],
        "really really really long group": ["1", "1", "1", "1", "1", "1", "1", "1",
                                            "1", "1", "1", "1", "1", "1", "1", "1",
                                            "1", "1", "1", "1", "1", "1", "1", "1",
                                            "1", "1", "1", "1", "1", "1", "1", "1",
                                            "1", "1", "1", "1", "1", "1", "1", "1",
                                            "1", "1", "1", "1", "1", "1", "1", "1",
                                            "1", "1", "1", "a", "1", "1", "1", "1",
                                            "1", "1", "1", "1", "1", "1", "1", "1",
                                            "1", "1", "1", "1", "1", "1", "1", "1"]
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #self.content_stack.add_titled(self.create_group_page("third"), "third", "third")

        # test = Gtk.Label()
        # test.set_text("test")
        # test.set_halign(Gtk.Align.START)

        # self.sidebar.insert(test, -1)

        self.populate_sidebar(self.test_data)

    # @Gtk.Template.Callback("stack_notify_visible_child_cb")
    # def stack_notify_visible_child_cb(self, sender, user_data):
    #     """Stack changed notifier callback.

    #     Hides the flap if it was opened and a new group was selected.

    #     Args:
    #         sender:     which object caused the callback to be triggered
    #         user_data:  optional user data (not used)
    #     """
    #     if self.main_flap.get_folded():
    #         self.main_flap.set_reveal_flap(False)

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

        row = sender.get_selected_row()

        self.populate_from_group(self.test_data, row.get_first_child().get_label())

    def populate_from_group(self, groups, name):
        """Populates main content.

        Args:
            groups: dict containing all groups and devices
            name:   name of the group to populate data from
        """
        self.clear_tiles()

        for device in groups[name]:
            tile = AmbienceTile()
            tile.top_label.set_label(device)

            self.light_tile_list.insert(tile, -1)

    def populate_sidebar(self, groups):
        """Populates sidebar list with groups.

        Args:
            groups: dict containing all groups and devices
        """
        self.clear_sidebar()

        for group in groups.keys():
            label = Gtk.Label()
            label.set_text(group)
            label.set_halign(Gtk.Align.START)

            self.sidebar.insert(label, -1)

    def clear_tiles(self):
        """Removes all tiles from tiles box."""

        while tile := self.light_tile_list.get_first_child():
            self.light_tile_list.remove(tile)

    def clear_sidebar(self):
        """Removes all entries from the sidebar."""

        while entry := self.sidebar.get_first_child():
            self.sidebar.remove(entry)

    def create_group_page(self, name):
        """Creates a widget consisting of tiles for a given group.

        Args:
            name: name of the group
        """
        flow = Gtk.FlowBox()
        flow.set_selection_mode(Gtk.SelectionMode.NONE)
        flow.set_homogeneous(True)

        # card = Gtk.Button()
        # card.add_css_class("card")
        # card.connect("clicked", clicked)
        # card.set_valign(Gtk.Align.START)

        # card_layout = Gtk.Grid()

        for i in range(100):
            tile = AmbienceTile()
            flow.insert(tile, -1)

        return flow
